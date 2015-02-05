class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.correct_recursive_argument = False

    def visit_If(self, node):
        super().visit_If(node)

        arg = self.functions['getdigits'].args[0]
        if arg is not None:
            self.correct_recursive_argument = \
                arg in TutorialNodeVisitor.involved_identifiers(node)


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['getdigits'].is_defined:
            self.add_error('getdigits is not defined')
        if not self.visitor.functions['getdigits'].calls['getdigits']:
            self.add_error('getdigits does not appear to be recursive')
        if not self.visitor.correct_recursive_argument:
            self.add_warning(
                'Your base case should probably check {}'.format(
                    self.visitor.functions['getdigits'].args[0]
                )
            )


ANALYSER = Analyser(CodeVisitor)
