class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_for = False
        self.iterates_over_arg = False

    def visit_For(self, node):
        super().visit_For(node)

        if self._current_function == 'has_gt':
            self.has_for = True

            iteration_id = TutorialNodeVisitor.identifier(node.iter)

            args = self.functions['has_gt'].args
            if args[0] is not None and iteration_id == args[0]:
                self.iterates_over_arg = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['has_gt'].is_defined:
            self.add_error('There is no definition of has_gt')
        elif len(self.visitor.functions['has_gt'].args) != 2:
            self.add_error('has_gt should accept exactly two arguments')
        elif not self.visitor.iterates_over_arg:
            self.add_warning('Your for loop should iterate over {}'.format(
                self.visitor.functions['has_gt'].args[0]
            ))

        if not self.visitor.has_for:
            self.add_error('Your function definition does not contain a for loop.')

        if not self.visitor.functions['has_gt'].returns:
            self.add_error('You need a return statement.')
        elif len(self.visitor.functions['has_gt'].returns) == 1:
            self.add_warning('You probably want to have two return statements')


ANALYSER = Analyser(CodeVisitor)
