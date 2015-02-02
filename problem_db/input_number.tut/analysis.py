class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic necessary


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions[None].calls['input']:
            self.add_error('You need to ask for input')
        elif not self.visitor.functions[None].calls['print']:
            self.add_error('You need to print something')
        elif not self.visitor.functions[None].calls['int']:
            self.add_warning('You probably need to use the int function')


ANALYSER = Analyser(CodeVisitor)