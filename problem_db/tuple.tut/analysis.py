class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.unpacks_tuple = False

    def visit_Assign(self, node):
        super().visit_Assign(node)

        if not len(node.targets):
            return

        if len(node.targets) > 1 or isinstance(node.targets[0], ast.Tuple):
            self.unpacks_tuple = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['get_names'].is_defined:
            self.add_error('You need to define a get_names function')
        elif len(self.visitor.functions['get_names'].args) != 0:
            self.add_error('get_names should accept no arguments')

        if not self.visitor.functions['get_names'].calls['input']:
            self.add_error('You need to get input from the user')
        if not self.visitor.functions['get_names'].calls['partition']:
            self.add_error('You need to use the str.partition method')

        if not self.visitor.unpacks_tuple:
            self.add_error('You need to use tuple unpacking')


ANALYSER = Analyser(CodeVisitor)