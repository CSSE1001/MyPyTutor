class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['square'].is_defined:
                self.add_error('You need to define the square function')
        elif len(self.visitor.functions['square'].args) != 1:
                self.add_error('square should accept exactly one argument')
        if not self.visitor.functions['square'].returns:
            self.add_error('You need a return statement')

        if self.visitor.functions['square'].calls['input']:
            self.add_error(
                "You don't need to call input; function arguments are passed "
                "automatically by Python"
            )



ANALYSER = Analyser(CodeVisitor)
