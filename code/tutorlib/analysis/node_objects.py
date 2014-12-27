from tutorlib.analysis.ast_tools import identifier, identifier_or_value
from tutorlib.analysis.support import NonePaddedList


class FunctionDefinition():
    def __init__(self, node=None):
        if node is None:
            self.is_defined = False
            return
        self.is_defined = True

        arg_ids = list(map(identifier, node.args.args))
        self.args = NonePaddedList(arg_ids)

        # TODO: kwargs, varargs etc


class ClassDefinition():
    def __init__(self, node=None):
        if node is None:
            self.is_defined = False
            return
        self.is_defined = True

        base_ids = list(map(identifier, node.bases))
        self.bases = base_ids

        # TODO: any other info from ClassDef which is relevant


class Call():
    def __init__(self, node):
        self.function_name = identifier(node.func)

        # TODO: .keywords, .starargs, .kwargs
        args = list(map(identifier_or_value, node.args))
        self.args = args

    def __repr__(self):
        return 'Call: {}({!r})'.format(self.function_name, self.args)
