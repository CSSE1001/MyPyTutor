import ast
from collections import defaultdict
import inspect

from tutorlib.analysis.ast_tools \
        import identifier, identifier_or_value, involved_identifiers, value
from tutorlib.analysis.node_objects \
        import Call, ClassDefinition, FunctionDefinition
from tutorlib.analysis.scope_manager import NodeScopeManager


class DefinesAllPossibleVisits(type):
    def __new__(mcs, clsname, bases, dct):
        is_node_class = lambda obj: inspect.isclass(obj) \
                and issubclass(obj, ast.AST) and obj is not ast.AST
        node_classes = inspect.getmembers(ast, is_node_class)

        generic_visit = dct.get('generic_visit', ast.NodeVisitor.generic_visit)
        base_has_method = lambda method_name: \
            any(getattr(base, method_name, None) is not None for base in bases)

        for name, node in node_classes:
            method_name = 'visit_{}'.format(name)

            # we want to alias generic_visit iff a specific visit_classname
            # method is not defined on this class, or on any parent class
            if method_name not in dct and not base_has_method(method_name):
                dct[method_name] = generic_visit

        return super().__new__(mcs, clsname, bases, dct)


class TutorialNodeVisitor(ast.NodeVisitor, metaclass=DefinesAllPossibleVisits):
    def __init__(self):
        self.functions = defaultdict(FunctionDefinition)
        self.classes = defaultdict(ClassDefinition)
        self.calls = defaultdict(list)  # str name : [Call]

        self._scopes = NodeScopeManager()

    # make support functions avaialble statically, so that it is only necessary
    # to inject this class into the analysis context
    identifier = identifier
    identifier_or_value = identifier_or_value
    involved_identifiers = involved_identifiers
    value = value

    @property
    def _current_function(self):
        return self._scopes.peek_function()

    @property
    def _current_class(self):
        return self._scopes.peek_class()

    def generic_visit(self, node):
        # disable the default logic in generic_visit (which is to recursively
        # traverse the tree), so that we only visit one node
        # instead, what we do is generate a list of all the nodes in the
        # desired format (using, eg, ListGeneratingNodeVisitor), and iterate
        # through that list, calling .visit
        # this approach is necessary because of problems with recursively
        # visiting nodes in both this class and subclasses
        # if we have a recursive visit in the superclass (ie this one) only,
        # either by using generic_visit or through the @visit_recursively
        # decorator, then we will visit child nodes before parent nodes (as
        # the call to super will logically occur before the overriden subclass
        # method does any of it swork)
        # if we call super later in the subclass method, then any logic which
        # is performed in the superclass method is unavailable to the subclass
        # one (which is problematic)
        # if we recurse in both the subclass and superclass methods, then we
        # visit nodes more than once (with exponential effects on deeply nested
        # chid nodes)
        pass

    def leave(self, node):
        method = 'leave_{}'.format(node.__class__.__name__)
        visitor = getattr(self, method, self.generic_leave)
        return visitor(node)

    def generic_leave(self, node):
        pass

    def visit_FunctionDef(self, node):
        function_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_function(function_name)

        # use the fully qualified function name from now on
        # if we're in a class, this will be, eg, ClassName.function_name
        function_name = self._scopes.current_scope_name

        # NB: we overwrite on repeated definition
        self.functions[function_name] = FunctionDefinition(node)

    def leave_FunctionDef(self, node):
        function_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_function_name = self._scopes.pop_function()

        assert popped_function_name == function_name, \
            'Leaving {}, but popped function was {}'.format(
                function_name, popped_function_name
            )

    def visit_ClassDef(self, node):
        class_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_class(class_name)

        # use teh fully qualified class name from now on
        # this will only be relevant for nested classes
        class_name = self._scopes.current_scope_name

        # again, overwrite on repeated definition
        self.classes[class_name] = ClassDefinition(node)

    def leave_ClassDef(self, node):
        class_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_class_name = self._scopes.pop_class()

        assert popped_class_name == class_name, \
            'Leaving {}, but popped class was {}'.format(
                class_name, popped_class_name
            )

    def visit_Call(self, node):
        function_name = TutorialNodeVisitor.identifier(node.func)
        # TODO: possibly track

        call = Call(node)
        self.calls[function_name].append(call)
