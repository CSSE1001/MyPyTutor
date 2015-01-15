class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_for_loop = False
        self.for_target_id = None
        self.iterates_over_arg = False

    def visit_For(self, node):
        super().visit_For(node)

        if self._current_function != 'filter_string':
            return

        self.has_for_loop = True

        arg = self.functions['filter_string'].args[0]
        if arg is not None:
            iterable_id = TutorialNodeVisitor.identifier(node.iter)
            self.iterates_over_arg = iterable_id == arg


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['filter_string'].is_defined:
            self.add_error('You need to define the filter_string function')
        elif len(self.visitor.functions['filter_string'].args) != 2:
            self.add_error('filter_string must accept exactly two arguments')

        if not self.visitor.has_for_loop:
            self.add_error('You need to use a for loop')
        elif not self.visitor.iterates_over_arg:
            self.add_warning(
                'You probably want to iterate over {}'.format(
                    self.visitor.functions['filter_string'].args[0]
                )
            )


ANALYSER = Analyser(CodeVisitor)