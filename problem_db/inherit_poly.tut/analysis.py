class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class Analyser(CodeAnalyser):
    def _analyse(self):
        num_expected_args = {
            'Rectangle.__init__': 3,
            'Rectangle.area': 1,
            'Rectangle.vertices': 1,
            'RightAngledTriangle.__init__': 2,
            'RightAngledTriangle.area': 1,
            'RightAngledTriangle.vertices': 1,
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

        if not self.visitor.functions['RightAngledTriangle.area'].calls['abs']:
            self.add_warning('abs may be useful in RightAngledTriangle.area')


ANALYSER = Analyser(CodeVisitor)