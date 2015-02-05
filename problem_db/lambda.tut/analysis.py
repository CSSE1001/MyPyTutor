class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class Analyser(CodeAnalyser):
    def _analyse(self):
        function_args = {
            'square': 1,
            'is_odd': 1,
            'add': 2,
        }
        fn = self.visitor.functions[None]

        for name, nargs in function_args.items():
            if not fn.assigns_to[name]:
                self.add_error(
                    'You need to write a lambda for {}'.format(name)
                )
            elif 'Lambda' not in str(type(fn.assigns_to[name][0])):
                # oh dear god that is so hacky
                self.add_error(
                    'You need to assign a lambda to {}'.format(name)
                )
            elif len(fn.assigns_to[name][0].args) != nargs:
                self.add_error(
                    '{} should take exactly {} arguments'.format(name, nargs)
                )


ANALYSER = Analyser(CodeVisitor)
