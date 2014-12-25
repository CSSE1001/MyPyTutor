class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_dec2base = False
        self.has_recursive_call = False

        self.checks_arg1_in_base_case = False

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        super().visit_FunctionDef(node)

        if TutorialNodeVisitor.identifier(node) == 'dec2base':
            self.has_dec2base = True

    @TutorialNodeVisitor.visit_recursively
    def visit_Call(self, node):
        super().visit_Call(node)

        if TutorialNodeVisitor.identifier(node.func) == 'dec2base':
            self.has_recursive_call = True

    @TutorialNodeVisitor.visit_recursively
    def visit_If(self, node):
        super().visit_If(node)

        arg = self.args['dec2base'][0]
        if arg is not None:
            self.checks_arg1_in_base_case = \
                    arg in TutorialNodeVisitor.involved_identifiers(node)


class RecursiveDigits2Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.has_dec2base:
            self.add_error('dec2base is not defined')
        if not self.visitor.has_recursive_call:
            self.add_error('dec2base does not appear to be recursive')
        if not self.visitor.checks_arg1_in_base_case:
            self.add_warning('Your base case should probably check {}'.format(self.visitor.args['dec2base'][0]))


ANALYSER = RecursiveDigits2Analyser(CodeVisitor)