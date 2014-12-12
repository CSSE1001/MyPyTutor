class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        self.has_dec2base = False
        self.has_recursive_call = False

        self.arg1 = None
        self.checks_arg1_in_base_case = False

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        if TutorialNodeVisitor.identifier(node) == 'dec2base':
            self.has_dec2base = True

    @TutorialNodeVisitor.visit_recursively
    def visit_arguments(self, arguments):
        # assume we're in dec2base
        # actually working tha out is not trivial with ast
        if len(arguments.args) == 2:
            self.arg1 = TutorialNodeVisitor.identifier(arguments.args[0])

    @TutorialNodeVisitor.visit_recursively
    def visit_Call(self, node):
        if TutorialNodeVisitor.identifier(node.func) == 'dec2base':
            self.has_recursive_call = True

    @TutorialNodeVisitor.visit_recursively
    def visit_If(self, node):
        if self.arg1 is not None:
            self.checks_arg1_in_base_case = \
                    self.arg1 in TutorialNodeVisitor.involved_identifiers(node)


class RecursiveDigits2Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.has_dec2base:
            self.add_error('dec2base is not defined')
        if not self.visitor.has_recursive_call:
            self.add_error('dec2base does not appear to be recursive')
        if not self.visitor.checks_arg1_in_base_case:
            self.add_warning('Your base case should probably check {}'.format(self.visitor.arg1))


ANALYSER = RecursiveDigits2Analyser(CodeVisitor)