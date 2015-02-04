class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_if_statement = False

    def visit_If(self, node):
        super().visit_If(node)

        self.has_if_statement = True


class DictAnalyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['get_value'].is_defined:
            self.add_error('You need to define a get_value function')
        elif len(self.visitor.functions['get_value'].args) != 2:
            self.add_error('get_value must accept exactly two args')

        if not self.visitor.functions['get_value'].calls['get']:
            self.add_error('You need to use the "get" method of your dictionary')

        if self.visitor.has_if_statement:
            self.add_error('You do not need to use an if statement')


ANALYSER = DictAnalyser(CodeVisitor)