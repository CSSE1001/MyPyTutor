import ast


class ListGeneratingNodeVisitor(ast.NodeVisitor):
    VISIT = 'VISIT'
    LEAVE = 'LEAVE'

    def __init__(self):
        self.events = []

    def generic_visit(self, node):
        self.events.append((ListGeneratingNodeVisitor.VISIT, node))
        super().generic_visit(node)
        self.events.append((ListGeneratingNodeVisitor.LEAVE, node))


class CodeAnalyser():
    def __init__(self, visitor_class):
        self.visitor = visitor_class()

        self.errors = []
        self.warnings = []

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def analyse(self, text):
        # build up an ordered list of nodes in the default manner
        tree = ast.parse(text)

        list_generating_visitor = ListGeneratingNodeVisitor()
        list_generating_visitor.visit(tree)

        # visit each node in turn with our visitor (which will not recurse)
        handle_event = {
            ListGeneratingNodeVisitor.VISIT: self.visitor.visit,
            ListGeneratingNodeVisitor.LEAVE: self.visitor.leave,
        }
        for event, node in list_generating_visitor.events:
            assert event in handle_event, 'Unknown event: {}'.format(event)
            handle_event[event](node)

        # defer detailed analysis to subclasses
        self._analyse()

    def _analyse(self):
        raise NotImplementedError()

    def check_for_errors(self, text):
        try:
            compile(text, '<student_code>', 'exec')
        except Exception as e:
            message = '{}: {}'.format(type(e).__name__, e)
            self.add_error(message)
            return getattr(e, 'lineno', None)

        return None
