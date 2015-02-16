class CodeVisitor(TutorialNodeVisitor):
    pass

class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['repeatedlyApply'].is_defined:
            self.add_error('You need to define repeatedlyApply')
        elif len(self.visitor.functions['repeatedlyApply'].args) != 2:
            self.add_error('repeatedlyApply should accept exactly two args')
        else:
            if not self.visitor.functions['repeatedlyApply'].calls['repeatedlyApply']:
                self.add_error('repeatedlyApply does not appear to be recursive')


ANALYSER = Analyser(CodeVisitor)
