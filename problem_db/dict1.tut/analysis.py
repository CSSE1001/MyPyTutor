class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        self.args = None
        self.subscripts_with_value = False

    @TutorialNodeVisitor.visit_recursively
    def visit_FunctionDef(self, node):
        if TutorialNodeVisitor.identifier(node) == 'get_value':
            self.args = list(map(
                TutorialNodeVisitor.identifier, node.args.args
            ))

    @TutorialNodeVisitor.visit_recursively
    def visit_Subscript(self, node):
        if self.args is not None and len(self.args) == 2:
            d, k = self.args

            if k in TutorialNodeVisitor.involved_identifiers(node.slice) \
                    and d == TutorialNodeVisitor.identifier(node.value):
                self.subscripts_with_value = True


class DictAnalyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if self.visitor.args is None:
            self.add_error('You need to define a get_value function')
        elif len(self.visitor.args) != 2:
            self.add_error('get_value must accept exactly two args')

        if not self.visitor.subscripts_with_value:
            self.add_error('You need to subscript the dictionary, eg d[k]')


ANALYSER = DictAnalyser(CodeVisitor)