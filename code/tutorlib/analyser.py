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
    def identifier(node):
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

        raise StaticAnalysisError(
            'No known identifier exists for node {}'.format(node)
        )
