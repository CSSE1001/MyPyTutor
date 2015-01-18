class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.initialises_variable = False
        self.initialises_to_zero = False

        self.has_for = False
        self.iteration_variable = None

    def visit_Assign(self, node):
        super().visit_Assign(node)

        if self._current_function == 'sum_elems' and not self.has_for:
            self.initialises_variable = True

            value = TutorialNodeVisitor.value(node.value)
            if value == 0:
                self.initialises_to_zero = True

    def visit_For(self, node):
        super().visit_For(node)

        if self._current_function == 'sum_elems':
            self.has_for = True

            self.iteration_variable = TutorialNodeVisitor.identifier(node.iter)


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['sum_elems'].is_defined:
            self.add_error('There is no definition of sum_elems')

        if self.visitor.functions['sum_elems'].calls['sum']:
            self.add_error('Your solution must not use sum')

        if not self.visitor.has_for:
            self.add_error(
                'Your function definition does not contain a for loop.'
            )
        if not self.visitor.functions['sum_elems'].returns:
            self.add_error('You need a return statement.')

        if not self.visitor.initialises_variable:
            self.add_error("You did't initialize before the for loop.")
        elif not self.visitor.initialises_to_zero:
            self.add_warning('You probably want to initialise to 0.')

        if self.visitor.functions['sum_elems'].is_defined \
                and (self.visitor.functions['sum_elems'].args[0] \
                     != self.visitor.iteration_variable):
            self.add_warning(
                'Your for loop should iterate over {}'.format(
                    self.visitor.functions['sum_elems'].args[0]
                )
            )


ANALYSER = Analyser(CodeVisitor)
