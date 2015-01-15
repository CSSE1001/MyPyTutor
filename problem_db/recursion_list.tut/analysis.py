class CodeVisitor(TutorialNodeVisitor):
    pass


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['recursive_index'].is_defined:
            self.add_error('recursive_index is not defined')

        if not self.visitor.functions['recursive_index']\
                .calls['recursive_index']:
            self.add_error('recursive_index does not appear to be recursive')


ANALYSER = Analyser(CodeVisitor)
