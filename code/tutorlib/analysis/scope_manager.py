class ScopeManagerError(Exception):
    '''
    Errors raised by the NodeScopeManager class.

    '''
    pass


class NodeScopeManager():
    """
    A class for managing nested scopes encountered when parsing a Python
    source file.

    Attributes:
      CLASS (constant): Identifier for a class scope.
      FUNCTION (constant): Identifier for a function scope.
      TYPES (constant): Exhaustive list of supported scope types.

      current_scope_name (str): The fully-qualified name of the current scope.

    """
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'
    TYPES = [CLASS, FUNCTION]

    def __init__(self):
        """
        Create a new NodeScopeManager object.

        """
        self._scopes = []  # (type, name), eg, (FUNCTION, do_stuff)

    @property
    def current_scope_name(self):
        """
        Return the fully-qualified name of the current scope.

        The meaning of this is best described by some examples.  For a function
        or class defined at module scope, this will be the function or class
        name itself:

            class ClassName():  -> 'ClassName'
                pass

            def function_name(): -> 'function_name'
                pass

        For a nested function or a nested class, this will consist of the names
        of all parent scopes, separated by periods, with the outermost scopes
        first:

            class ClassName():
                def method():  -> 'ClassName.method'
                    pass

                class NestedClass():  -> 'ClassName.NestedClass'
                    def f(): -> 'ClassName.NestedClass.f'
                        pass

            def function_name():
                def inner_function():  -> 'function_name.inner_function'
                    pass

                class NestedClass():  -> 'function_name.NestedClass'
                    pass

        Note that methods are nested functions.

        """
        return '.'.join(name for tpe, name in self._scopes)

    def append(self, name, tpe):
        """
        Add a scope with the given name and type to the stack.

        Args:
          name (str): The name of the scope to add.
          tpe (constant): The type of the scope to add.  Must be one of .TYPES

        """
        assert tpe in self.TYPES, 'Unknown type: {}'.format(tpe)
        self._scopes.append((tpe, name))

    def pop(self, tpe):
        """
        Pop a scope of the given type.

        The top scope will always be popped, *not* the highest scope of the
        given type (the latter would not make much sense, as it would leave the
        stack in an inconsistent state).

        Args:
          tpe (constant): The type of the scope to pop.

        Returns:
          The unqualified name of the topmost scope.

        Raises:
          ScopeManagerError: If the type of the topmost scope is not the same
            as the given type, or if there are no scopes to pop.

        """
        if not self._scopes:
            raise ScopeManagerError('There are no scopes to pop!')

        pop_tpe, name = self._scopes.pop()

        if tpe != pop_tpe:
            raise ScopeManagerError(
                'Popped {} of type {}, but expected type {}'.format(
                    name, pop_tpe, tpe
                )
            )

        return name

    def peek(self, tpe):
        """
        Return the fully-qualified name of the current scope, iff it is of the
        given type.

        Args:
          tpe (constant): The type of the scope to peek att.

        Returns:
          The fully-qualified name of the current scope, if that scope is of
          the given type.

          None if the current scope is not of the given type.  This is an
          intentional asymmetry with pop, as it is useful to peek and see that
          the current scope is *not* of the specified type.

          None if there are no scopes on the stack.  This is an intentional
          asymmetry with pop (which raises an exception in such cases).

        """
        if not self._scopes:
            return None

        peek_tpe, name = self._scopes[-1]

        if tpe != peek_tpe:
            return None

        return self.current_scope_name

    def append_class(self, name):
        """
        Append a .CLASS scope with the given name.

        Args:
          name (str): The name of the scope to append.

        """
        self.append(name, NodeScopeManager.CLASS)

    def pop_class(self):
        """
        Pop a .CLASS scope.

        For return values and possible exceptions, see .pop

        """
        return self.pop(NodeScopeManager.CLASS)

    def peek_class(self):
        """
        Peek at a .CLASS scope.

        For return values, see .peek

        """
        return self.peek(NodeScopeManager.CLASS)

    def append_function(self, name):
        """
        Append a .FUNCTION scope with the given name.

        Args:
          name (str): The name of the scope to append.

        """
        self.append(name, NodeScopeManager.FUNCTION)

    def pop_function(self):
        """
        Pop a .FUNCTION scope.

        For return values and possible exceptions, see .pop

        """
        return self.pop(NodeScopeManager.FUNCTION)

    def peek_function(self):
        """
        Peek at a .FUNCTION scope.

        For return values, see .peek

        """
        return self.peek(NodeScopeManager.FUNCTION)
