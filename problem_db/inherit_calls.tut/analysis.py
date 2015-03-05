class CodeVisitor(TutorialNodeVisitor):
    pass


class Analyser(CodeAnalyser):
    def _analyse(self):
        if len(self.visitor.functions[None].calls['print']) != 4:
            self.add_error('You should use exactly four print statements')


ANALYSER = Analyser(CodeVisitor)
