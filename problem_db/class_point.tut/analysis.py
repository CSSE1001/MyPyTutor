class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class PointAnalyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.classes['Point'].is_defined:
            self.add_error('You need to define the Point class')

        num_expected_args = {
            'Point.__init__': 3,
            'Point.dist_to_point': 2,
            'Point.is_near': 2,
            'Point.add_point': 2,
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


ANALYSER = PointAnalyser(CodeVisitor)
