import ast
from collections import defaultdict
from collections.abc import Sequence
from functools import wraps
import inspect
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
        # build up an ordered list of nodes in the default manner
        tree = ast.parse(text)

        list_generating_visitor = ListGeneratingNodeVisitor()
        list_generating_visitor.visit(tree)

        # visit each node in turn with our visitor (which will not recurse)
        handle_event = {
            ListGeneratingNodeVisitor.VISIT: self.visitor.visit,
            ListGeneratingNodeVisitor.LEAVE: self.visitor.leave,
        }
        for event, node in list_generating_visitor.events:
            assert event in handle_event, 'Unknown event: {}'.format(event)
            handle_event[event](node)

        # defer detailed analysis to subclasses
        self._analyse()

    def _analyse(self):
        raise NotImplementedError()

    def check_for_errors(self, text):
        try:
            compile(text, '<student_code>', 'exec')
        except Exception as e:
            message = '{}: {}'.format(type(e).__name__, e)
            self.add_error(message)
            return getattr(e, 'lineno', None)

        return None


class NonePaddedList(Sequence):
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
        self._data = list(iterable)

    def __repr__(self):
        return 'NonePaddedList({!r})'.format(self._data)

    def __getitem__(self, item):
        if item < len(self):
            return self._data[item]
        return None

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        # default __iter__ implementation uses try/except on successive
        # __getitem__ calls, but because we return None for invalid indices
        # we will never actually cause the exception
        # instead, make use of the fact that len(self) is defined
        for idx in range(len(self)):
            yield self[idx]


class ListGeneratingNodeVisitor(ast.NodeVisitor):
    VISIT = 'VISIT'
    LEAVE = 'LEAVE'

    def __init__(self):
        self.events = []

    def generic_visit(self, node):
        self.events.append((ListGeneratingNodeVisitor.VISIT, node))
        super().generic_visit(node)
        self.events.append((ListGeneratingNodeVisitor.LEAVE, node))


class NodeScopeManager():
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'
    TYPES = [CLASS, FUNCTION]

    def __init__(self):
        self._scopes = []  # (type, name), eg, (FUNCTION, do_stuff)

    @property
    def current_scope_name(self):
        return '.'.join(name for tpe, name in self._scopes)

    def append(self, name, tpe):
        assert tpe in self.TYPES, 'Unknown type: {}'.format(tpe)
        self._scopes.append((tpe, name))

    def pop(self, tpe):
        pop_tpe, name = self._scopes.pop()

        assert tpe == pop_tpe, \
            'Popped {} of type {}, but expected type {}'.format(
                name, pop_tpe, tpe
            )

        # note that popping gives back the unqualified name (as that is what
        # was appended in the first place)
        return name

    def peek(self, tpe):
        if not self._scopes:
            return None

        # we could get the type wrong here as well
        # however, in the context of a peek, this isn't necessarily an error,
        # because it just means that we're *not* in a function/class/etc
        peek_tpe, name = self._scopes[-1]

        if tpe != peek_tpe:
            return None

        # give back the *fully qualified name*
        # clients needs to be aware of this, but it's more flexible
        return self.current_scope_name

    def append_class(self, name):
        self.append(name, NodeScopeManager.CLASS)

    def pop_class(self):
        return self.pop(NodeScopeManager.CLASS)

    def peek_class(self):
        return self.peek(NodeScopeManager.CLASS)

    def append_function(self, name):
        self.append(name, NodeScopeManager.FUNCTION)

    def pop_function(self):
        return self.pop(NodeScopeManager.FUNCTION)

    def peek_function(self):
        return self.peek(NodeScopeManager.FUNCTION)


class FunctionDefinition():
    def __init__(self, node=None):
        if node is None:
            self.is_defined = False
            return
        self.is_defined = True

        arg_ids = list(map(TutorialNodeVisitor.identifier, node.args.args))
        self.args = NonePaddedList(arg_ids)

        # TODO: kwargs, varargs etc


class DefinesAllPossibleVisits(type):
    def __new__(mcs, clsname, bases, dct):
        is_node_class = lambda obj: inspect.isclass(obj) \
                and issubclass(obj, ast.AST) and obj is not ast.AST
        node_classes = inspect.getmembers(ast, is_node_class)

        generic_visit = dct.get('generic_visit', ast.NodeVisitor.generic_visit)
        base_has_method = lambda method_name: \
            any(getattr(base, method_name, None) is not None for base in bases)

        for name, node in node_classes:
            method_name = 'visit_{}'.format(name)

            # we want to alias generic_visit iff a specific visit_classname
            # method is not defined on this class, or on any parent class
            if method_name not in dct and not base_has_method(method_name):
                dct[method_name] = generic_visit

        return super().__new__(mcs, clsname, bases, dct)


class TutorialNodeVisitor(ast.NodeVisitor, metaclass=DefinesAllPossibleVisits):
    def __init__(self):
        self.functions = defaultdict(FunctionDefinition)
        self.classes = defaultdict(NonePaddedList)  # class_name : bases

        self._scopes = NodeScopeManager()

    @property
    def _current_function(self):
        return self._scopes.peek_function()

    @property
    def _current_class(self):
        return self._scopes.peek_class()

    def generic_visit(self, node):
        # disable the default logic in generic_visit (which is to recursively
        # traverse the tree), so that we only visit one node
        # instead, what we do is generate a list of all the nodes in the
        # desired format (using, eg, ListGeneratingNodeVisitor), and iterate
        # through that list, calling .visit
        # this approach is necessary because of problems with recursively
        # visiting nodes in both this class and subclasses
        # if we have a recursive visit in the superclass (ie this one) only,
        # either by using generic_visit or through the @visit_recursively
        # decorator, then we will visit child nodes before parent nodes (as
        # the call to super will logically occur before the overriden subclass
        # method does any of it swork)
        # if we call super later in the subclass method, then any logic which
        # is performed in the superclass method is unavailable to the subclass
        # one (which is problematic)
        # if we recurse in both the subclass and superclass methods, then we
        # visit nodes more than once (with exponential effects on deeply nested
        # chid nodes)
        pass

    def leave(self, node):
        method = 'leave_{}'.format(node.__class__.__name__)
        visitor = getattr(self, method, self.generic_leave)
        return visitor(node)

    def generic_leave(self, node):
        pass

    def visit_FunctionDef(self, node):
        function_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_function(function_name)

        # use the fully qualified function name from now on
        # if we're in a class, this will be, eg, ClassName.function_name
        function_name = self._scopes.current_scope_name

        # NB: this ignores varargs, kwargs etc
        # NB: we overwrite on repeated definition
        self.functions[function_name] = FunctionDefinition(node)

    def leave_FunctionDef(self, node):
        function_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_function_name = self._scopes.pop_function()

        assert popped_function_name == function_name, \
                'Leaving {}, but popped function was {}'.format(
                    function_name, popped_function_name
                )

    def visit_ClassDef(self, node):
        class_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_class(class_name)

        # use teh fully qualified class name from now on
        # this will only be relevant for nested classes
        class_name = self._scopes.current_scope_name

        # grab bases (superclasses)
        # again, overwrite on repeated definition
        base_ids = list(map(TutorialNodeVisitor.identifier, node.bases))
        self.classes[class_name] = NonePaddedList(base_ids)

    def leave_ClassDef(self, node):
        class_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_class_name = self._scopes.pop_class()

        assert popped_class_name == class_name, \
                'Leaving {}, but popped class was {}'.format(
                    class_name, popped_class_name
                )

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
    def involved_identifiers(*nodes):
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
        identifiers = []

        for node in nodes:
            if not isinstance(node, ast.AST):
                raise StaticAnalysisError(
                    'TutorialNodeVisitor.involved_identifiers must be '
                    'called on ast nodes (got {!r} instead).  Did you mean '
                    'to call this method with *varargs?  You called it with '
                    '{!r} instead'.format(node, nodes)
                )

            # if this node has an identifier, start out with that
            this_identifier = TutorialNodeVisitor.identifier(
                node, suppress_exceptions=True
            )
            if this_identifier is not None:
                identifiers.append(this_identifier)

            # set up what attrs we want to recurse on
            # this is not always everything (eg, on a FunctionDef we don't want
            # to consider the 'body' as having involved identifiers)
            recurse_on = {
                # stmt
                ast.FunctionDef: ['args'],
                ast.ClassDef: ['bases'],

                ast.Delete: ['targets'],
                ast.Assign: ['targets', 'value'],
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
                continue

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
                    child_ids = TutorialNodeVisitor.involved_identifiers(
                        child_node
                    )
                    identifiers.extend(child_ids)

        return identifiers
