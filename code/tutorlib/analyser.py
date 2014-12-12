import ast


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
