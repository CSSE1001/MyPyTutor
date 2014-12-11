import ast


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 1
        self.seen_inc = []
        self.seen_double = []
        self.did_assign = False
        self.in_assign = False

    def visit_Call(self, t):
        if self.in_assign:
            if t.func.id == 'double':
                self.seen_double.append(self.count)
                self.count += 1
            elif t.func.id == 'increment':
                self.seen_inc.append(self.count)
                self.count += 1
            for arg in t.args:
                self.visit(arg)

    def visit_Assign(self, t):
        if t.targets[0].id == 'm':
            self.in_assign = True
            self.did_assign = True
            self.visit(t.value)
            self.in_assign = False


class Fun1Analyser(CodeAnalyser):
    def analyse(self, text):
        astree = ast.parse(text)
        self.visitor.visit(astree)

        if not self.visitor.did_assign:
            self.add_error("You have not assigned to the variable m")
        if len(self.visitor.seen_double) == 0:
            self.add_error("You need to use the double function in your single assignment statement")
        if len(self.visitor.seen_inc) == 0:
            self.add_error("You need to use the increment function in your single assignment statement")
        if len(self.visitor.seen_double) > 1:
            self.add_error("You only need to use double once")
        if len(self.visitor.seen_inc) > 1:
            self.add_error("You only need to use increment once")
        if self.visitor.seen_double[0] > self.visitor.seen_inc[0]:
            self.add_error("You should be using increment inside the use of double")


ANALYSER = Fun1Analyser(CodeVisitor)