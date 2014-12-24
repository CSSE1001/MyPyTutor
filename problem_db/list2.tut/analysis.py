class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        self.is_defined = False
        self.in_def = False
        self.arg1 = None

        self.initialises_variable = False

        self.has_for = False
        self.iteration_variable = None

        self.appends_in_loop = False
        self.appends_outside_loop = False

        self.has_return = False

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        if TutorialNodeVisitor.identifier(node) == 'all_gt':
            self.is_defined = True
            self.in_def = True
        else:
            self.in_def = False

    @TutorialNodeVisitor.visit_recursively
    def visit_arguments(self, arguments):
        if self.in_def:
            if len(arguments.args) == 2:
                self.arg1 = TutorialNodeVisitor.identifier(arguments.args[0])

    @TutorialNodeVisitor.visit_recursively
    def visit_Assign(self, node):
        if self.in_def and not self.has_for:
            self.initialises_variable = True

            # TODO: check value using node.value.elts
            # TODO: not done atm, as checking for _ast.List is hacky

    @TutorialNodeVisitor.visit_recursively
    def visit_For(self, node):
        if self.in_def:
            self.has_for = True

            self.iteration_variable = TutorialNodeVisitor.identifer(node.iter)

    @TutorialNodeVisitor.visit_recursively
    def visit_Call(self, node):
        if TutorialNodeVisitor.identifier(node.func) == 'append':
            if self.in_def and self.has_for:
                self.appends_in_loop = True
            elif self.in_def:
                self.appends_outside_loop = True

    @TutorialNodeVisitor.visit_recursively
    def visit_Return(self, node):
        self.has_return = True


class List2Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.is_defined:
            self.add_error('There is no definition of all_gt')
        if not self.visitor.has_for:
            self.add_error('Your function definition does not contain a for loop.')
        if not self.visitor.has_return:
            self.add_error('You need a return statement.')
        if not self.visitor.initialises_variable:
            self.add_error("You did't initialize before the for loop.")
        if self.visitor.appends_outside_loop:
            self.add_error("You want to append inside the loop, not outside it.")
        if not self.visitor.appends_in_loop:
            self.add_error("You need to append inside the for loop.")
        if self.visitor.arg1 != self.visitor.iteration_variable:
            self.add_warning('Your for loop should iterate over {}'.format(self.visitor.arg1))


ANALYSER = List2Analyser(CodeVisitor)