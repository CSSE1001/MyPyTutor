class CodeVisitor(TutorialNodeVisitor):
    pass  # no special logic needed


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['base2dec'].is_defined:
            self.add_error('You need to define base2dec')
        elif len(self.visitor.functions['base2dec'].args) != 2:
            self.add_error('base2dec should accept exactly two arguments')

        if not self.visitor.functions['base2dec'].calls['base2dec']:
            self.add_error('base2dec must be recursive')


ANALYSER = Analyser(CodeVisitor)