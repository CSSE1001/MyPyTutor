class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.uses_in = False

        self.for_loop_count = 0
        self.iterates_over_second_arg = False

    def visit_In(self, node):
        super().visit_In(node)

        self.uses_in = True

    def visit_For(self, node):
        super().visit_For(node)

        if not self.for_loop_count:
            self.for_loop_count += 1

            target_id = TutorialNodeVisitor.identifier(node.iter)
            if target_id == self.functions['occurrences'].args[1]:
                self.iterates_over_second_arg = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['occurrences'].is_defined:
            self.add_error('You need to define an occurrences function')
        elif len(self.visitor.functions['occurrences'].args) != 2:
            self.add_error('occurrences should accept exactly 2 arguments')

        if not self.visitor.iterates_over_second_arg:
            self.add_error(
                'Your for loop should iterate over the second argument'
            )

        if not self.visitor.uses_in:
            self.add_warning('You should probably use the in keyword')

        if self.visitor.for_loop_count > 1:
            self.add_warning('This problem is easiest with a single for loop')


ANALYSER = Analyser(CodeVisitor)