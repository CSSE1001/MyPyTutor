class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class RectAnalyser(CodeAnalyser):
    def _analyse(self):
        if 'Rectangle' not in self.visitor.classes:
            self.add_error('You need to define the Rectangle class')

        num_expected_args = {
            'Rectangle.__init__': 4,
            'Rectangle.get_bottom_right': 1,
            'Rectangle.move': 2,
            'Rectangle.resize': 3,
            'Rectangle.__str__': 1,
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


ANALYSER = RectAnalyser(CodeVisitor)