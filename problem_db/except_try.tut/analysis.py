class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        self.has_try_except = False
        self.excepts_value_error = False
        self.excepts_exception = False

    def visit_ExceptHandler(self, node):
        super().visit_ExceptHandler(node)

        self.has_try_except = True

        exception_type_id = TutorialNodeVisitor.identifier(node.type)
        if exception_type_id == 'ValueError':
            self.excepts_value_error = True
        elif exception_type_id == 'Exception':
            self.excepts_exception = True


class Analyser(CodeAnalyser):
    def _analyse(self):
        if not self.visitor.functions['try_int'].is_defined:
            self.add_error('You need to define a try_int function')
        elif len(self.visitor.functions['try_int'].args) != 1:
            self.add_error('try_int should accept exactly 1 arguments')

        if not self.visitor.functions['try_int'].calls['int']:
            self.add_error(
                'Your code should make use of the built-in int function'
            )

        if not self.visitor.has_try_except:
            self.add_error('You need a try/except statement')
        elif not self.visitor.excepts_value_error:
            self.add_error('You need to except ValueError{}'.format(
                ' (not Exception)' if self.visitor.excepts_exception else ''
            ))


ANALYSER = Analyser(CodeVisitor)
