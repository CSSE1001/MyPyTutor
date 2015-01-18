import ast
from collections import defaultdict
from functools import partial

from tutorlib.analysis.ast_tools \
    import fully_qualified_identifier, identifier, identifier_or_value
from tutorlib.analysis.support import AutoHashingDefaultDict, NonePaddedList


class FunctionDefinition():
    """
    A description of a function definition in the Python grammar, built from
    an ast.FunctionDef node.

    Attributes:
      is_defined (bool): Whether the function has been defined.
      args (NonePaddedList<str>): The identifiers of the arguments to the
          function.
      assigns_to ({Identifier: [object]}): The identifiers which have been
          assigned to in the function.  Identifiers are unordered, but the
          successive assignments for each identifier are in the order
          encountered.
      assigned_value_of ({object: [Identifier]}): The identifiers which have
          had the value in question assigned to them in the fuction.
      calls (defaultdict<str:[Call]>): All functions called in the code, as
          Call objects.  The list of calls is in the order encountered by the
          visitor (by default, depth first).  Quering the defaultdict for
          functions which were not called will return an empty list.
      returns ([object]): Values returned from the function, in the order
          encountered.

    """
    def __init__(self, node=None):
        """
        Create a new FunctionDefinition object.

        Note that the FunctionDefinition object does not keep track of the
        name of the function, as this would not exist for an undefined
        function.  This class must therefore be used in conjunction with some
        kind of mapping.

        Args:
          node (ast.FunctionDef, optional): The node to create the function
              definition for.  Defaults to None.  If None, then the function
              will be marked as undefined.

        """
        assert node is None or isinstance(node, ast.FunctionDef)

        if node is None:
            self.is_defined = False

            self.args = NonePaddedList()
        else:
            self.is_defined = True

            arg_ids = list(map(identifier, node.args.args))
            self.args = NonePaddedList(arg_ids)

            # TODO: kwargs, varargs etc

        self.calls = defaultdict(list)  # str name : [Call]

        self.assigns_to = AutoHashingDefaultDict(list)  # ident : [object]
        self.assigned_value_of = AutoHashingDefaultDict(list)  # object:[ident]

        self.returns = []


class ClassDefinition():
    """
    A description of a class definition in the Python grammar, built from an
    ast.ClassDef node.

    Attributes:
      is_defined (bool): Whether the class has been defined.
      bases ([str]): The identifiers of the class's bases, if any.

    """
    def __init__(self, node=None):
        """
        Create a new ClassDefinition object.

        Note that the ClassDefinition object does not keep track of the name
        of the class, as this would not exist for an undefined class.  This
        class must therefore be used in conjunction with some kind of mapping.

        Args:
          node (ast.ClassDef, optional): The node to create the class
              definition for.  Defaults to None.  If None, then the class will
              be marked as undefined.

        """
        assert node is None or isinstance(node, ast.ClassDef)

        if node is None:
            self.is_defined = False

            self.bases = []
        else:
            self.is_defined = True

            base_ids = list(map(identifier, node.bases))
            self.bases = base_ids

            # TODO: any other info from ClassDef which is relevant


class Call():
    """
    A description of a call in the Python grammar, built from an ast.Call node.

    Attributes:
      function_name (str): The identifier of the called function.
      args ([object]): The arguments to the called function.  These will be
        python objects in the case of literals, strs in the case of
        identifiers, and None otherwise.  Note that it is currently impossible
        to distinguish between identifiers and literal strings.

    """
    def __init__(self, node):
        """
        Create a new Call object.

        Args:
          node (ast.Call): The node to create the Call object for.

        """
        assert isinstance(node, ast.Call)

        self.function_name = fully_qualified_identifier(node.func)

        # TODO: .starargs, .kwargs
        args = list(map(identifier_or_value, node.args))
        self.args = args

        silent_id = partial(identifier, suppress_exceptions=True)
        silent_id_or_val = partial(
            identifier_or_value,
            prefer_value=True,
            fully_qualified=True,
        )

        self.keywords = {
            silent_id(kw.arg): silent_id_or_val(kw.value)
                    for kw in node.keywords
        }

    def __repr__(self):
        args = ', '.join(map(str, self.args))
        kwds = ', '.join(
            '='.join(map(str, items)) for items in self.keywords.items()
        )
        return '{}({}{})'.format(
            self.function_name,
            args,
            '{}{}'.format(', ' if args else '', kwds) if kwds else ''
        )

    def __eq__(self, other):
        if not isinstance(other, Call):
            return False

        return self.function_name == other.function_name \
                and self.args == other.args \
                and self.keywords == other.keywords

    def __hash__(self):
        return hash((
            self.function_name,
            tuple(self.args),
            tuple(self.keywords.items()),
        ))
