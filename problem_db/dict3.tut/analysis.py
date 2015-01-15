class CodeVisitor(TutorialNodeVisitor):
    pass


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['add_to_dict'].is_defined:
            self.add_error('You need to define a add_to_dict function')
        elif len(self.visitor.functions['add_to_dict'].args) != 2:
            self.add_error('add_to_dict should accept exactly 2 arguments')
        elif not self.visitor.functions['add_to_dict'].calls['append']:
            self.add_warning('You probably want to use list.append')


ANALYSER = Analyser(CodeVisitor)