class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class Analyser(CodeAnalyser):
    def _analyse(self):
        pass  # TODO


ANALYSER = Analyser(CodeVisitor)