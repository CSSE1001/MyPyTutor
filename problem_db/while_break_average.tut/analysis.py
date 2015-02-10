class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_while_statement = False
        self.has_break_statement = False

    def visit_While(self, node):
        super().visit_If(node)
        self.has_while_statement = True

    def visit_Break(self, node):
        self.has_break_statement = True

class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.has_while_statement:
            self.add_error('You need to use a while statement')
        elif not self.visitor.has_break_statement:
            self.add_error('You need to use a break statement')
ANALYSER = Analyser(CodeVisitor)
