import ast
from operator import attrgetter


class StaticAnalysisError(Exception):
    pass


class CodeAnalyser():
    def __init__(self, visitor_class):
        self.visitor = visitor_class()

        self.errors = []
        self.warnings = []

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def analyse(self, text):
        raise NotImplementedError()

    def check_for_errors(self, text):
        try:
            compile(text, '<student_code>', 'exec')
        except Exception as e:
            message = '{}: {}'.format(type(e).__name__, e)
            self.add_error(message)
            return getattr(e, 'lineno', None)

        return None


class TutorialNodeVisitor(ast.NodeVisitor):
    @staticmethod
    def visit_recursively(fn):
        # see http://stackoverflow.com/a/14661325/1103045
        # keep on CodeAnalyser namespace to limit injections to analysis.py
        def wrapper(self, node):
            result = fn(self, node)

            for child in ast.iter_child_nodes(node):
                self.visit(child)

            return result
        return wrapper

    @staticmethod
    def identifier(node, suppress_exceptions=False):
        '''
        TutorialNodeVisitor.identifier(ast._AST) -> str

        Depending on the context, an ast node may store the relevant identifier
        on one of a number of properties.  This is a direct consequence of the
        grammar (see the ast documentation).

        There's two ways we could try to deal with this:
          (1) search for attrs, trying each in turn until we find one
          (2) use the grammar the 'know' what an attr should be

        The latter is preferable, as the grammar is limited, and we therefore
        know the mappings ahead of time (ie, there's no need to treat ast nodes
        as if they could be duck typed).

        There are potential issues here if isinstance plays up due to two
        versions of the ast module being imported (for whatever reason), but
        that should be caught by the trailing exception.  In other words, if
        this exception is raised, that's probably why.

        '''
        mappings = {
            # stmt
            ast.FunctionDef: attrgetter('name'),
            ast.ClassDef: attrgetter('name'),

            # expr
            ast.Attribute: attrgetter('attr'),
            ast.Name: attrgetter('id'),

            # other top-level grammar constructs
            ast.excepthandler: attrgetter('name'),
            ast.arg: attrgetter('arg'),
            ast.keyword: attrgetter('arg'),
            ast.alias: attrgetter('name'),
        }

        if type(node) in mappings:
            return mappings[type(node)](node)

        if suppress_exceptions:
            return None

        raise StaticAnalysisError(
            'No known identifier exists for node {}'.format(node)
        )

    @staticmethod
    def involved_identifiers(node):
        '''
        TutorialNodeVisitor.involved_identifiers(ast._AST) -> [str]

        Return a list of all identifiers involved in a statement or expression.

        It's often necessary to check if a student has used a particular
        identifier in a particular context.

        Depending on the type of node, this can be quite an involved process.
        For example, a student might write extremely convoluted if statements,
        where we expect only a simple one.

        This method will recursively determine all identifiers which have been
        used in a statement, regardless of the complexity of the ast tree.

        '''
        # if this node has an identifier, start out with that
        this_identifier = TutorialNodeVisitor.identifier(
            node, suppress_exceptions=True
        )
        identifiers = [this_identifier] if this_identifier is not None else []

        # set up what attrs we want to recurse on
        # this is not always everything (eg, on a FunctionDef we don't want to
        # consider the 'body' as having involved identifiers)
        recurse_on = {
            # stmt
            ast.FunctionDef: ['args'],
            ast.ClassDef: ['bases'],

            ast.Delete: ['targets'],
            ast.Assign: ['targets'],
            ast.AugAssign: ['target', 'value'],

            ast.For: ['target', 'iter'],
            ast.While: ['test'],
            ast.If: ['test'],
            ast.With: ['items'],

            ast.Assert: ['test', 'msg'],

            ast.Import: ['names'],
            ast.ImportFrom: ['names'],

            ast.Expr: ['value'],

            # expr
            ast.BoolOp: ['values'],
            ast.BinOp: ['left', 'right'],
            ast.UnaryOp: ['operand'],
            ast.Lambda: ['args'],
            ast.IfExp: ['test'],
            ast.Dict: ['keys', 'values'],
            ast.Set: ['elts'],
            ast.ListComp: ['generators'],
            ast.SetComp: ['generators'],
            ast.DictComp: ['generators'],
            ast.GeneratorExp: ['generators'],

            ast.Yield: ['value'],
            ast.YieldFrom: ['value'],

            ast.Compare: ['left', 'comparators'],
            ast.Call: ['func', 'args', 'keywords', 'starargs', 'kwargs'],

            ast.Attribute: ['value'],
            ast.Subscript: ['value', 'slice'],
            ast.Starred: ['value'],
            ast.List: ['elts'],
            ast.Tuple: ['elts'],

            # slice
            ast.Slice: ['lower', 'upper', 'step'],
            ast.ExtSlice: ['dims'],
            ast.Index: ['value'],

            # comprehension
            ast.comprehension: ['target', 'iter', 'ifs'],

            # arguments, arg, keyword
            ast.arguments: ['args', 'vararg', 'kwonlyargs', 'kw_defaults',
                            'kwarg', 'defaults'],
            ast.arg: ['annotation'],
            ast.keyword: ['value'],

            # withitem
            ast.withitem: ['context_expr', 'optional_vars'],
        }

        # if we don't have anything to recurse on, we're done
        if type(node) not in recurse_on:
            return identifiers

        # recursively check for identifiers
        # note that some of the attrs (eg ClassDef.bases) are themselves
        # sequences; because ast seems to always use list for these, we can
        # just check for that
        for attr_name in recurse_on[type(node)]:
            attr_value = getattr(node, attr_name)

            if isinstance(attr_value, list):
                child_nodes = attr_value
            else:
                child_nodes = [attr_value]

            # certain attrs are optional; ignore them if they're None
            child_nodes = filter(None, child_nodes)

            for child_node in child_nodes:
                child_identifiers = TutorialNodeVisitor.involved_identifiers(
                    child_node
                )
                identifiers.extend(child_identifiers)

        return identifiers
