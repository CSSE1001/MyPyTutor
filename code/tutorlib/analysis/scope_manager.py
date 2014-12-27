class NodeScopeManager():
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'
    TYPES = [CLASS, FUNCTION]

    def __init__(self):
        self._scopes = []  # (type, name), eg, (FUNCTION, do_stuff)

    @property
    def current_scope_name(self):
        return '.'.join(name for tpe, name in self._scopes)

    def append(self, name, tpe):
        assert tpe in self.TYPES, 'Unknown type: {}'.format(tpe)
        self._scopes.append((tpe, name))

    def pop(self, tpe):
        pop_tpe, name = self._scopes.pop()

        assert tpe == pop_tpe, \
            'Popped {} of type {}, but expected type {}'.format(
                name, pop_tpe, tpe
            )

        # note that popping gives back the unqualified name (as that is what
        # was appended in the first place)
        return name

    def peek(self, tpe):
        if not self._scopes:
            return None

        # we could get the type wrong here as well
        # however, in the context of a peek, this isn't necessarily an error,
        # because it just means that we're *not* in a function/class/etc
        peek_tpe, name = self._scopes[-1]

        if tpe != peek_tpe:
            return None

        # give back the *fully qualified name*
        # clients needs to be aware of this, but it's more flexible
        return self.current_scope_name

    def append_class(self, name):
        self.append(name, NodeScopeManager.CLASS)

    def pop_class(self):
        return self.pop(NodeScopeManager.CLASS)

    def peek_class(self):
        return self.peek(NodeScopeManager.CLASS)

    def append_function(self, name):
        self.append(name, NodeScopeManager.FUNCTION)

    def pop_function(self):
        return self.pop(NodeScopeManager.FUNCTION)

    def peek_function(self):
        return self.peek(NodeScopeManager.FUNCTION)
