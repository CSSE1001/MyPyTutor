class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.lambda_count = 0
        self.num_lambda_args = None
        self.adds_in_lambda = False

    def visit_Lambda(self, node):
        super().visit_Lambda(node)

        self.lambda_count += 1
        self.num_lambda_args = len(node.args.args)

        if isinstance(node.body, ast.BinOp) \
                and isinstance(node.body.op, ast.Add):
            self.adds_in_lambda = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['add_functions'].is_defined:
            self.add_error('You need to define add_functions')
        elif len(self.visitor.functions['add_functions'].args) != 2:
            self.add_error('add_functions should accept exactly two args')
        else:
            # some of these are only safe if the function is defined properly
            if self.visitor.lambda_count == 0:
                self.add_error('You need to use a lambda function')
            elif self.visitor.lambda_count > 1:
                self.add_error('You only need to define one lambda function')
            elif self.visitor.num_lambda_args != 1:
                self.add_error('Your lambda should only take in a single arg')
            elif not self.visitor.adds_in_lambda:
                self.add_error('Your lambda should add the results of f and g')

            fn = self.visitor.functions['add_functions']

            if not all(arg in fn.calls for arg in fn.args):
                self.add_warning(
                    "It looks like you're not calling both {} and {} in "
                    "your lambda function".format(*fn.args)
                )


ANALYSER = Analyser(CodeVisitor)
