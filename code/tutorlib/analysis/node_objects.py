import ast

from tutorlib.analysis.ast_tools import identifier, identifier_or_value
from tutorlib.analysis.support import NonePaddedList


class FunctionDefinition():
    """
    A description of a function definition in the Python grammar, built from
    an ast.FunctionDef node.

    Attributes:
      is_defined (bool): Whether the function has been defined.
      args (NonePaddedList<str>): The identifiers of the arguments to the
          function.

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
        assert isinstance(node, ast.FunctionDef)

        if node is None:
            self.is_defined = False
            return
        self.is_defined = True

        arg_ids = list(map(identifier, node.args.args))
        self.args = NonePaddedList(arg_ids)

        # TODO: kwargs, varargs etc


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
        assert isinstance(node, ast.ClassDef)

        if node is None:
            self.is_defined = False
            return
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

        self.function_name = identifier(node.func)

        # TODO: .keywords, .starargs, .kwargs
        args = list(map(identifier_or_value, node.args))
        self.args = args

    def __repr__(self):
        return 'Call: {}({!r})'.format(self.function_name, self.args)
