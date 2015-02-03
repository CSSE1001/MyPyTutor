class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_if_statement = False
        self.has_else_statement = False

    def visit_If(self, node):
        super().visit_If(node)

        self.has_if_statement = True
        self.has_else_statement = not not node.orelse


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.has_if_statement:
            self.add_error('You need to use an if statement')
        elif not self.visitor.has_else_statement:
            self.add_error('Your if statment needs an else')
        elif not self.visitor.functions[None].calls['is_vowel']:
            self.add_warning('You probably want to use the is_vowel function')


ANALYSER = Analyser(CodeVisitor)