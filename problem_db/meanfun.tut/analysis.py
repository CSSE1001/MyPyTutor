class CodeVisitor(TutorialNodeVisitor):
    pass  # no additional logic needed


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['mean'].is_defined:
            self.add_error('You need to define the mean function')
        elif len(self.visitor.functions['mean'].args) != 1:
            self.add_error('mean should accept exactly one argument')


ANALYSER = Analyser(CodeVisitor)