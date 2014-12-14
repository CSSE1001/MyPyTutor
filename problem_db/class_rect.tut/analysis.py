class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        self.defined_class = False

        methods = (
            '__init__',
            'get_bottom_right',
            'move',
            'resize',
            '__str__',
        )

        self.method_args = {k: None for k in methods}

    @TutorialNodeVisitor.visit_recursively
    def visit_ClassDef(self, node):
        if TutorialNodeVisitor.identifier(node) == 'Rectangle':
            self.defined_class = True

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        function_name = TutorialNodeVisitor.identifier(node)

        if function_name in self.method_args:
            # in Python 3, you can't unpack tuples in arguments (PEP 3113)
            # the number of involved identifiers will therefore always be equal
            # to the argument count
            arg_names = TutorialNodeVisitor.involved_identifiers(node.args)
            self.method_args[function_name] = arg_names


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

        for method_name, args in self.visitor.method_args.items():
            if args is None:
                self.add_error(
                    'You need to define a {} method'.format(method_name)
                )
            elif 'self' not in args:
                self.add_warning(
                    'The first argument to a method should be \'self\''
                )
            elif len(args) != num_expected_args[method_name]:
                self.add_error(
                    'You defined {} to accept {} arguments, but it should ' \
                    'accept {} (including self)'.format(
                        method_name, len(args), num_expected_args[method_name]
                    )
                )


ANALYSER = RectAnalyser(CodeVisitor)