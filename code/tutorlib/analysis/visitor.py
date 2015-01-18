import ast
from collections import defaultdict
import inspect

from tutorlib.analysis.ast_tools \
        import fully_qualified_identifier, identifier, identifier_or_value, \
               involved_identifiers, value
from tutorlib.analysis.node_objects \
        import Call, ClassDefinition, FunctionDefinition
from tutorlib.analysis.scope_manager import NodeScopeManager
from tutorlib.analysis.support import AutoHashingDefaultDict


class DefinesAllPossibleVisits(type):
    """
    Metaclass for ast.NodeVisitor subclasses which aliases all possible
    concrete visits to .generic_visit

    This is necessary so that subclasses of the class in question can safely
    call super() on any concrete visit_ClassName method.

    Without this metaclass (or something similar), subclasses would need to be
    aware exactly which visit_ClassName methods the class in question overrode
    at any given point in time.

    """
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
    """
    Custom ast.NodeVisitor subclass for visiting student code.

    This class automatically builds up some useful information on the node tree
    without any additional work needed on the part of superclasses.

    Attributes:
      functions (defaultdict<str:FunctionDefinition>): All functions defined in
          the code, as FunctionDefinition objects.  Quering the defaultdict for
          undefined functions will return a FunctionDefinition object with
          .is_defined = False
      classes (defaultdict<str:ClassDefinition>): All classes defined in the
          code, as ClassDefinition objects.  Quering the defaultdict for
          undefined classes will return a ClassDefinition object with
          .is_defined = False
      calls (defaultdict<str:[Call]>): All functions called in the code, as
          Call objects.  The list of calls is in the order encountered by the
          visitor (by default, depth first).  Quering the defaultdict for
          functions which were not called will return an empty list.

    """
    def __init__(self):
        self.functions = defaultdict(FunctionDefinition)
        self.classes = defaultdict(ClassDefinition)
        self.calls = defaultdict(list)  # str name : [Call]

        self.assignments_to = AutoHashingDefaultDict(list)  # ident : [object]
        self.assignments_of = AutoHashingDefaultDict(list)  # object : [ident]

        self._scopes = NodeScopeManager()

    # make support functions avaialble statically, so that it is only necessary
    # to inject this class into the analysis context
    fully_qualified_identifier = fully_qualified_identifier
    identifier = identifier
    identifier_or_value = identifier_or_value
    involved_identifiers = involved_identifiers
    value = value

    @property
    def _current_function(self):
        return self._scopes.peek_function()

    @property  # NB: intended to be *really* private ;)
    def _current_function_def(self):
        return self.functions[self._current_function]

    def generic_visit(self, node):
        """
        Do nothing.

        This intentionally disables the default logic in .generic_visit (which
        is to recursively traverse the tree), so that we only visit nodes which
        are explicitly passed as arguments to .visit (or which are otherwise
        visited by the resulting visit_ClassName calls).

        What we do instead is generate a list of all the nodes in the desired
        format (using ListGeneratingNodeVisitor, or some other means), and then
        iterate through that list, calling .visit on each.

        THis approach is necessary because of problems with recursively
        visiting nodes in both this class and its subclasses.

        If we have a recursive visit in the superclass (ie, this one) only,
        either by using generic_visit or through a decorator like the old
        @visit_recursively one, we will visit child nodes before parent nodes
        (as the subclass will call super() prior to its own logic for the
        current node, and thus set off the recursive visit).

        On the other hand, if we call super later in the subclass method,
        rather than at the start as would be normal, then any logic which is
        performed in the superclass method (ie, the overriden visit_ClassName
        methods defined here) will be unavailable to the subclass.

        Finally, if we recurse in both the subclass and the superclass methods,
        then we will visit nodes more than once (exponentially so in the case
        of deeply nested child nodes).

        So we do nothhing.

        Args:
          node (ast.AST): The node to do absolutely nothing with.

        """
        pass

    def leave(self, node):
        """
        Custom equivalent of .visit, called when we leave a node.

        This implementation is based off the ast.NodeVisitor.visit source code.
        It will defer to .leave_ClassName, if defined, or otherwise to
        .generic_leave

        Args:
          node (ast.AST): The node we are leaving.

        Returns:
          Whatever the .leave_ClassName or .generic_visit method returns
          (probably None).

        """
        method = 'leave_{}'.format(node.__class__.__name__)
        visitor = getattr(self, method, self.generic_leave)
        return visitor(node)

    def generic_leave(self, node):
        """
        Do nothing.

        There is no special logic required for leaving a node.

        Args:
          node (ast.AST): The node we are leaving.

        """
        pass

    def visit_FunctionDef(self, node):
        """
        Default logic for visiting a FunctionDef node.

        Add the function to our stack of scopes, and record the function
        details (via a FunctionDefinition object) in .functions

        Args:
          node (ast.FunctionDef): The node we are visiting.

        """
        function_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_function(function_name)

        # use the fully qualified function name from now on
        # if we're in a class, this will be, eg, ClassName.function_name
        function_name = self._scopes.current_scope_name

        # NB: we overwrite on repeated definition
        self.functions[function_name] = FunctionDefinition(node)

    def leave_FunctionDef(self, node):
        """
        Default logic for leaving a FunctionDef node.

        Remove the function from our stack of scopes.

        Args:
          node (ast.FunctionDef): The node we are leaving.

        """
        function_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_function_name = self._scopes.pop_function()

        assert popped_function_name == function_name, \
            'Leaving {}, but popped function was {}'.format(
                function_name, popped_function_name
            )

    def visit_ClassDef(self, node):
        """
        Default logic for visiting a ClassDef node.

        Add the class to our stack of scopes, and record the class details
        (via a ClassDef object) in .classes

        Args:
          node (ast.ClassDef): The node we are visiting.

        """
        class_name = TutorialNodeVisitor.identifier(node)

        # add this to our scopes
        self._scopes.append_class(class_name)

        # use teh fully qualified class name from now on
        # this will only be relevant for nested classes
        class_name = self._scopes.current_scope_name

        # again, overwrite on repeated definition
        self.classes[class_name] = ClassDefinition(node)

    def leave_ClassDef(self, node):
        """
        Default logic for leaving a ClassDef node.

        Remove the class from our stack of scopes.

        Args:
          node (ast.ClassDef): The node we are leaving.

        """
        class_name = TutorialNodeVisitor.identifier(node)

        # remove this from our scopes
        popped_class_name = self._scopes.pop_class()

        assert popped_class_name == class_name, \
            'Leaving {}, but popped class was {}'.format(
                class_name, popped_class_name
            )

    def visit_Assign(self, node):
        """
        Default logic for visiting an Assign node.

        Record information about the assignment in assignments_to (mapping the
        target var to its assigned value) and in assignments_of (mapping the
        assigned value to the target var).

        Args:
          node (ast.Assign): The node we are visiting.

        """
        for target_id in map(identifier, node.targets):
            if target_id is None:
                continue

            if isinstance(node.value, ast.Call):
                assignment_value = Call(node.value)
            else:
                assignment_value = identifier_or_value(node, prefer_value=True)

            # always set assignments_to, but only set assignments_of if we
            # have a known value (to avoid lots of None entries)
            self.assignments_to[target_id].append(assignment_value)

            if assignment_value is not None:
                self.assignments_of[assignment_value].append(target_id)

    def visit_Call(self, node):
        """
        Default logic for visiting a Call node.

        Record information about the call in .calls, using a Call object.

        Args:
          node (ast.Call): The node we are visiting.

        """
        function_name = TutorialNodeVisitor.identifier(node.func)

        call = Call(node)
        self.calls[function_name].append(call)

        self._current_function_def.calls[function_name].append(call)
