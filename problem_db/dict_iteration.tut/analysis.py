class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_for = False
        self.iteration_variable = None

    def visit_For(self, node):
        super().visit_For(node)

        if self._current_function == 'big_keys':
            self.has_for = True

            self.iteration_variable = TutorialNodeVisitor.identifier(node.iter)


class DictAnalyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['big_keys'].is_defined:
            self.add_error('You need to define a big_keys function')
        elif len(self.visitor.functions['big_keys'].args) != 2:
            self.add_error('big_keys must accept exactly two args')

        if not self.visitor.has_for:
            self.add_error(
                'Your function definition does not contain a for loop.'
            )
        else:
            if self.visitor.functions['big_keys'].is_defined \
               and (self.visitor.functions['big_keys'].args[0] \
                    != self.visitor.iteration_variable):
                self.add_warning(
                    'Your for loop should iterate over {}'.format(
                        self.visitor.functions['big_keys'].args[0]
                    )
                )

        if not self.visitor.functions['big_keys'].returns:
            self.add_error('You need a return statement.')


ANALYSER = DictAnalyser(CodeVisitor)
