class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['repeatedly_apply'].is_defined:
            self.add_error('You need to define repeatedly_apply')
        elif len(self.visitor.functions['repeatedly_apply'].args) != 2:
            self.add_error('repeatedly_apply should accept exactly two args')
        else:
            if not self.visitor.functions['repeatedly_apply'].calls['repeatedly_apply']:
                self.add_error('repeatedly_apply does not appear to be recursive')


ANALYSER = Analyser(CodeVisitor)
