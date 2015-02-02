class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_if_statement = False

    def visit_If(self, node):
        super().visit_If(node)

        self.has_if_statement = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.has_if_statement:
            self.add_error('You need to use an if statement')
        elif not self.visitor.functions[None].calls['int']:
            self.add_warning('You probably want to use the int function')


ANALYSER = Analyser(CodeVisitor)