class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.uses_comprehension = False
        self.uses_if_comprehension = False

    def visit_ListComp(self, node):
        super().visit_ListComp(node)
        self.uses_comprehension = True
        if node.generators[0].ifs != []:
            self.uses_if_comprehension = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['square_odds'].is_defined:
            self.add_error('You need to define square_odds')
        elif len(self.visitor.functions['square_odds'].args) != 1:
            self.add_error('square_odds should accept exactly one arg')
        else:
            if not self.visitor.uses_comprehension:
                self.add_error('You need to use list comprehension')
            if not self.visitor.uses_if_comprehension:
                self.add_error('You need to use if inside list comprehension')


ANALYSER = Analyser(CodeVisitor)
