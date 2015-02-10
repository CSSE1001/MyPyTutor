class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()
        self.has_while_statement = False

    def visit_While(self, node):
        self.has_while_statement = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['div_3_5'].is_defined:
                self.add_error('You need to define the div_3_5 function')
        elif len(self.visitor.functions['div_3_5'].args) != 2:
                self.add_error('div_3_5 should accept exactly two arguments')
        if not self.visitor.has_while_statement:
            self.add_error('You need to use a while statement')
        if not self.visitor.functions['div_3_5'].returns:
            self.add_error('You need a return statement')



ANALYSER = Analyser(CodeVisitor)
