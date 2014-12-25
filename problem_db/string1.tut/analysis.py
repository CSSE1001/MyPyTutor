class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.input_count = 0
        self.print_count = 0

    @TutorialNodeVisitor.visit_recursively
    def visit_Call(self, node):
        super().visit_Call(node)

        func_name = TutorialNodeVisitor.identifier(node.func)

        if func_name == 'input':
            self.input_count += 1
        elif func_name == 'print':
            self.print_count += 1


class String1Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.input_count:
            self.add_error('You need to prompt for a string using input()')
        elif self.visitor.input_count > 1:
            self.add_error('You should only be prompting for a single input')

        if self.visitor.print_count != 3:
            self.add_warning('You should have three print statements')


ANALYSER = String1Analyser(CodeVisitor)