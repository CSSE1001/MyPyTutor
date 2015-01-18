class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_for_loop = False
        self.for_target_id = None
        self.iterates_over_arg = False

        self.checks_correct_var = False

    def visit_For(self, node):
        super().visit_For(node)

        if self._current_function != 'get_digits':
            return

        self.has_for_loop = True
        self.for_target_id = TutorialNodeVisitor.identifier(node.target)

        arg = self.functions['get_digits'].args[0]
        if arg is not None:
            iterable_id = TutorialNodeVisitor.identifier(node.iter)
            self.iterates_over_arg = iterable_id == arg

    def visit_Call(self, node):
        super().visit_Call(node)

        if self._current_function != 'get_digits':
            return

        function_name = TutorialNodeVisitor.identifier(node.func)

        if function_name == 'isdigit':
            identifiers = TutorialNodeVisitor.involved_identifiers(node)

            if self.for_target_id in identifiers:
                self.checks_correct_var = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['get_digits'].is_defined:
            self.add_error('You need to define the function get_digits')
        elif len(self.visitor.functions['get_digits'].args) != 1:
            self.add_error('get_digits should accept exactly one argument')

        if not self.visitor.has_for_loop:
            self.add_warning('You should use a for loop in get_digits')
        elif not self.visitor.iterates_over_arg \
                and self.visitor.functions['get_digits'].args[0] is not None:
            self.add_warning(
                'Your for loop should iterate over {}'.format(
                    self.visitor.functions['get_digits'].args[0]
                )
            )

        if not self.visitor.functions['get_digits'].calls['isdigit']:
            self.add_error('You should use str.isdigit')
        elif not self.visitor.checks_correct_var:
            self.add_warning(
                'You should be checking if {} is a digit'.format(
                    self.visitor.for_target_id
                )
            )

ANALYSER = Analyser(CodeVisitor)