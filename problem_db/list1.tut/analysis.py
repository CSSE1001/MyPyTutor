class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self._in_has_gt = False

        self.has_for = False
        self.iterates_over_arg = False

        self.return_count = 0

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        super().visit_FunctionDef(node)

        if TutorialNodeVisitor.identifier(node) == 'has_gt':
            self._in_has_gt = True

    @TutorialNodeVisitor.visit_recursively
    def visit_For(self, node):
        super().visit_For(node)

        if self._in_has_gt:
            self.has_for = True

            iteration_id = TutorialNodeVisitor.identifier(node.iter)

            args = self.args['has_gt']
            if args[0] is not None and iteration_id == args[0]:
                self.iterates_over_arg = True

    @TutorialNodeVisitor.visit_recursively
    def visit_Return(self, node):
        super().visit_Return(node)

        self.return_count += 1


class Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if self.visitor.args['has_gt'] is None:
            self.add_error('There is no definition of has_gt')
        elif len(self.visitor.args['has_gt']) != 2:
            self.add_error('has_gt should accept exactly two arguments')
        elif not self.visitor.iterates_over_arg:
            self.add_warning('Your for loop should iterate over {}'.format(
                self.visitor.args[0]
            ))

        if not self.visitor.has_for:
            self.add_error('Your function definition does not contain a for loop.')

        if not self.visitor.return_count:
            self.add_error('You need a return statement.')
        elif self.visitor.return_count == 1:
            self.add_warning('You probably want to have two return statements')


ANALYSER = Analyser(CodeVisitor)
