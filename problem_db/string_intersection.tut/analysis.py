class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_return = False
        self.iterates_over_first_arg = False

    def visit_For(self, node):
        super().visit_For(node)

        target_id = TutorialNodeVisitor.identifier(node.iter)
        if target_id == self.functions['intersection'].args[0]:
            self.iterates_over_first_arg = True

    def visit_Return(self, node):
        super().visit_Return(node)

        self.has_return = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['intersection'].is_defined:
            self.add_error('You need to define an intersection function')
        elif len(self.visitor.functions['intersection'].args) != 2:
            self.add_error('intersection should accept exactly two arguments')

        if not self.visitor.has_return:
            self.add_error('You need a return statement')

        if not self.visitor.iterates_over_first_arg:
            self.add_warning(
                'You should iterate over the first argument using a for loop'
            )


ANALYSER = Analyser(CodeVisitor)