class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.slice_from_slices = False
        self.reverse_string_slices = False

    def visit_Slice(self, node):
        super().visit_Slice(node)

        if self._current_function == 'slice_from':
            self.slice_from_slices = True
        elif self._current_function == 'reverse_string':
            self.reverse_string_slices = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        num_expected_args = [
            ('slice_from', 3),
            ('reverse_string', 1),
        ]

        # check functions are defined and accept the right number of args
        for function_name, argc in num_expected_args:
            function = self.visitor.functions[function_name]

            if not function.is_defined:
                self.add_error('You need to define {}'.format(function_name))
            elif len(function.args) != argc:
                self.add_error('{} should accept exactly {} args'.format(
                    function_name, argc
                ))

            if function.calls['input']:
                self.add_error(
                    "You don't need to call input; function arguments are "
                    "passed automatically by Python"
                )

        if not self.visitor.slice_from_slices:
            self.add_error('You need to use a slice in slice_from')
        if not self.visitor.reverse_string_slices:
            self.add_error('You need to use a slice in reverse_string')


ANALYSER = Analyser(CodeVisitor)
