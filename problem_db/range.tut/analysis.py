class CodeVisitor(TutorialNodeVisitor):
    pass


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['sum_range'].is_defined:
            self.add_error('You need to define a sum_range function')
        elif len(self.visitor.functions['sum_range'].args) != 2:
            self.add_error('sum_range must accept exactly two arguments')

        if not self.visitor.functions['sum_range'].calls['range']:
            self.add_error('sum_range must call range')

        if not self.visitor.functions['sum_evens'].is_defined:
            self.add_error('You need to define a sum_evens function')
        elif len(self.visitor.functions['sum_evens'].args) != 2:
            self.add_error('sum_evens must accept exactly two arguments')

        if not self.visitor.functions['sum_evens'].calls['range']:
            self.add_error('sum_evens must call range')


ANALYSER = Analyser(CodeVisitor)