# TODO: static analysis: check that the variable exists and has the right value.

class InputAnalyser(CodeAnalyser):
    def _analyse(self):
        pass

ANALYSER = InputAnalyser(TutorialNodeVisitor)
