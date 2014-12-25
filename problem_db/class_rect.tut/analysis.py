class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.defined_class = False

    @TutorialNodeVisitor.visit_recursively
    def visit_ClassDef(self, node):
        super().visit_ClassDef(node)

        if TutorialNodeVisitor.identifier(node) == 'Rectangle':
            self.defined_class = True


class RectAnalyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.defined_class:
            self.add_error('You need to define the Rectangle class')

        num_expected_args = {
            '__init__': 4,
            'get_bottom_right': 1,
            'move': 2,
            'resize': 3,
            '__str__': 1,
        }

        for method_name, argc in num_expected_args.items():
            args = self.visitor.args[method_name]

            if args is None:
                self.add_error(
                    'You need to define a {} method'.format(method_name)
                )
            elif 'self' not in args:
                self.add_warning(
                    'The first argument to a method should be \'self\''
                )
            elif len(args) != argc:
                self.add_error(
                    'You defined {} to accept {} arguments, but it should ' \
                    'accept {} (including self)'.format(
                        method_name, len(args), num_expected_args[method_name]
                    )
                )


ANALYSER = RectAnalyser(CodeVisitor)