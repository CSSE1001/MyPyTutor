class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.count = 1
        self.seen_inc = []
        self.seen_double = []

    def visit_Call(self, node):
        super().visit_Call(node)

        func_name = TutorialNodeVisitor.identifier(node.func)
        if func_name == 'double':
            self.seen_double.append(self.count)
            self.count += 1
        elif func_name == 'increment':
            self.seen_inc.append(self.count)
            self.count += 1


class Fun1Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions[None].calls['input']:
            self.add_error('You need to prompt the user for input')
        elif not self.visitor.functions[None].calls['print']:
            self.add_error('You need to print something')
        elif not self.visitor.functions[None].calls['int']:
            self.add_warning('You probably want to use the int function')

        if not self.visitor.functions[None].calls['double']:
            self.add_error('You need to call double')
        elif not self.visitor.functions[None].calls['increment']:
            self.add_error('You need to call increment')

        if len(self.visitor.functions[None].calls['double']) > 1:
            self.add_error("You only need to use double once")
        if len(self.visitor.functions[None].calls['increment']) > 1:
            self.add_error("You only need to use increment once")

        if self.visitor.seen_double and self.visitor.seen_inc \
                and self.visitor.seen_double[0] > self.visitor.seen_inc[0]:
            self.add_error(
                'You should be using increment inside the use of double'
            )


ANALYSER = Fun1Analyser(CodeVisitor)