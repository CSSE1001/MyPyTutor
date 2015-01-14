class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.worker_init_calls_super = False
        self.executive_init_calls_super = False

        self.executive_wage_calls_super = False

    def visit_Call(self, node):
        super().visit_Call(node)

        function_name = TutorialNodeVisitor.identifier(node.func)

        if self._current_function == 'Worker.__init__' \
                and function_name == '__init__':
            self.worker_init_calls_super = True
        if self._current_function == 'Executive.__init__' \
                and function_name == '__init__':
            self.executive_init_calls_super = True

        if self._current_function == 'Executive.wage':
            if function_name == 'wage':
                self.executive_wage_calls_super = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        for cls_name in ['Worker', 'Executive']:
            if not self.visitor.classes[cls_name].is_defined:
                self.add_error(
                    'You need to define the {} class'.format(cls_name)
                )
            elif 'Employee' not in self.visitor.classes[cls_name].bases:
                self.add_error(
                    '{} must inherit from Employee'.format(cls_name)
                )
            elif len(self.visitor.classes[cls_name].bases) > 1:
                self.add_error(
                    '{} must *only* inherit from Employee'.format(cls_name)
                )

        num_expected_args = {
            'Worker.__init__': 4,
            'Worker.get_manager': 1,
            'Executive.__init__': 4,
            'Executive.wage': 1,
        }

        for method_name, argc in num_expected_args.items():
            function = self.visitor.functions[method_name]

            if not function.is_defined:
                self.add_error(
                    'You need to define a {} method'.format(method_name)
                )
            elif 'self' not in function.args:
                self.add_warning(
                    'The first argument to a method should be \'self\''
                )
            elif len(function.args) != argc:
                self.add_error(
                    'You defined {} to accept {} arguments, but it should '
                    'accept {} (including self)'.format(
                        method_name, len(function.args), argc
                    )
                )

        if not self.visitor.worker_init_calls_super:
            self.add_error(
                'Worker.__init__ must call Employee.__init__ (use super)'
            )
        if not self.visitor.executive_init_calls_super:
            self.add_error(
                'Executive.__init__ must call Employee.__init__ (use super)'
            )

        if not self.visitor.executive_wage_calls_super:
            self.add_error(
                'Executive.wage must call Employee.wage (use super)'
            )


ANALYSER = Analyser(CodeVisitor)