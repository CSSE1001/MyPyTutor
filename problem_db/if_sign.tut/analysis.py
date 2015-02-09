class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_if_statement = False
        self.has_elif_statement = False
        self.has_else_statement = False

    def visit_If(self, node):
        super().visit_If(node)
        if not self.has_if_statement and node.orelse:
            if '_ast.If' in str(type(node.orelse[0])):
                self.has_elif_statement = True
                if node.orelse[0].orelse:
                    self.has_else_statement = True
            else:
                self.has_else_statement = True
        self.has_if_statement = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.has_if_statement:
            self.add_error('You need to use an if statement')
        elif not self.visitor.has_elif_statement:
            self.add_error('Your if statment needs an elif')
        elif not  self.visitor.has_else_statement:
            self.add_error('Your if statment needs an else')


ANALYSER = Analyser(CodeVisitor)
