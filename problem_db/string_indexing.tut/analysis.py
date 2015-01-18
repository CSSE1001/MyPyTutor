class CodeVisitor(TutorialNodeVisitor):
    pass  # No special code needed


class String1Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions[None].calls['input']:
            self.add_error('You need to prompt for a string using input()')
        elif len(self.visitor.functions[None].calls['input']) > 1:
            self.add_error('You should only be prompting for a single input')

        if len(self.visitor.functions[None].calls['print']) != 3:
            self.add_warning('You should have three print statements')


ANALYSER = String1Analyser(CodeVisitor)