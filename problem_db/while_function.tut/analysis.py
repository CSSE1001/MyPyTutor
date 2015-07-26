class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()
        self.has_while_statement = False
        self.in_while = False
        self.return_in_while = False
        self.has_return = False

    def visit_While(self, node):
        self.has_while_statement = True
        self.in_while = True

    def leave_While(self, node):
        self.in_while = False

    def visit_Return(self, node):
        self.has_return = True
        if self.in_while:
            self.return_in_while = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['div_3_5'].is_defined:
                self.add_error('You need to define the div_3_5 function')
        elif len(self.visitor.functions['div_3_5'].args) != 2:
                self.add_error('div_3_5 should accept exactly two arguments')
        if not self.visitor.has_while_statement:
            self.add_error('You need to use a while statement')

        if not self.visitor.has_return:
            self.add_error('You need a return statement')
        elif self.visitor.return_in_while:
            self.add_warning(
                'You proably don\'t want a return statement inside the '
                'while loop'
            )

        if self.visitor.functions['div_3_5'].calls['input']:
            self.add_error(
                "You don't need to call input; function arguments are passed "
                "automatically by Python"
            )


ANALYSER = Analyser(CodeVisitor)
