# TODO: does this problem need any static analysis? probably not.

class InputAnalyser(CodeAnalyser):
    def _analyse(self):
        pass

ANALYSER = InputAnalyser(TutorialNodeVisitor)
