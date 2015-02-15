class CodeVisitor(TutorialNodeVisitor):
    super().__init__()
    self.rec_call = False
    self.rec_arg = None
    self.if_arg = None
    self.in_if = False
    self.in_compare = False


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['repeatedlyApply'].is_defined:
            self.add_error('You need to define repeatedlyApply')
        elif len(self.visitor.functions['repeatedlyApply'].args) != 2:
            self.add_error('repeatedlyApply should accept exactly two args')
        else:
            if not self.visitor.functions['repeatedlyApply'].calls['repeatedlyApply']:
                self.add_error('repeatedlyApply does not appear to be recursive')

            if not self.visitor.uses_comprehension:
                self.add_error('You need to use list comprehension')
            if not self.visitor.uses_if_comprehension:
                self.add_error('You need to use if inside list comprehension')


ANALYSER = Analyser(CodeVisitor)
