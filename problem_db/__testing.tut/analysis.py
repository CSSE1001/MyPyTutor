# No static analysis required.

class HelloAnalyser(CodeAnalyser):
    def _analyse(self):
        pass

ANALYSER = HelloAnalyser(TutorialNodeVisitor)
