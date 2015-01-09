import ast
from functools import partial
from operator import attrgetter

from tutorlib.analysis.support import StaticAnalysisError


def identifier(node, suppress_exceptions=False):
    """
    Return the identifier of the given node.

    In this context, an identifier is considered to be equivalent to a
    reference, a variable, or an object.  Certain ast nodes contain multiple
    identifiers (for example, ast.Attribute will have an identifier both for
    the attribute and the associated value).  In those cases, only one such
    identifier will be returned.  See the source code for details.

    Depending on the context, an ast node may store the relevant identifier
    on one of a number of properties.  This is a direct consequence of the
    grammar (see the ast documentation).

    There's two ways we could try to deal with this:
      (1) search for attrs, trying each in turn until we find one
      (2) use the grammar the 'know' what an attr should be

    The latter is preferable, as the grammar is limited, and we therefore
    know the mappings ahead of time (ie, there's no need to treat ast nodes
    as if they could be duck typed).

    There are potential issues here if isinstance plays up due to two
    versions of the ast module being imported (for whatever reason), but
    that should be caught by the trailing exception.  In other words, if
    this exception is raised, that's probably why.

    Args:
      node (ast.Node): The node to return the identifier of.
      suppress_exceptions (bool, optional): Whether exceptions should be
          suppressed.  If True, then this method will return None if an
          identifier cannot be found.  Defaults to False.

    Returns:
      The identifier of the node, as a str.

      If the node has no defined identifier (according to the rules used in
      this function), and suppress_exceptions is True, then None will be
      returned.

    Raises:
      StaticAnalysisError: If the node has no defined identifier (according to
          the rules used in this function), and suppress_exceptions is False.

    """
    mappings = {
        # stmt
        ast.FunctionDef: attrgetter('name'),
        ast.ClassDef: attrgetter('name'),

        # expr
        ast.Attribute: attrgetter('attr'),
        ast.Name: attrgetter('id'),

        # other top-level grammar constructs
        ast.excepthandler: attrgetter('name'),
        ast.arg: attrgetter('arg'),
        ast.keyword: attrgetter('arg'),
        ast.alias: attrgetter('name'),
    }

    if type(node) in mappings:
        return mappings[type(node)](node)

    if suppress_exceptions:
        return None

    raise StaticAnalysisError(
        'No known identifier exists for node {}'.format(node)
    )


def involved_identifiers(*nodes):
    """
    Return a list of all identifiers involved in a statement or expression.

    This method attempts to return *all* of the involved identifiers, and so
    its result will *not* be equivalent to that of the identifier function.
    See the source code for a description of the node properties which are
    considered to be identifiers.

    It's often necessary to check if a student has used a particular
    identifier in a particular context.

    Depending on the type of node, this can be quite an involved process.
    For example, a student might write extremely convoluted if statements,
    where we expect only a simple one.

    This method will recursively determine all identifiers which have been
    used in a statement, regardless of the complexity of the ast tree.

    Args:
      *nodes (ast.AST, ...): A variable-length arguments list of the nodes to
          return identifiers for.

    Returns:
      A list of all involved identifiers, as strings.

      The order of this list is not defined.

    Raises:
      StaticAnalysisError: If any variable-length argument is not a subclass
          of ast.AST (ie, is not a node).  Duck typing is therefore not
          supported, but the advantage is that common errors (such as passing
          a list in place of *nodes) will be caught immediately.

    """
    identifiers = []

    for node in nodes:
        if not isinstance(node, ast.AST):
            raise StaticAnalysisError(
                'involved_identifiers must be called on ast nodes.  '
                'Did you mean to call this method with *varargs?  '
                'You called it with {!r} instead'.format(node)
            )

        # if this node has an identifier, start out with that
        this_identifier = identifier(node, suppress_exceptions=True)
        if this_identifier is not None:
            identifiers.append(this_identifier)

        # set up what attrs we want to recurse on
        # this is not always everything (eg, on a FunctionDef we don't want
        # to consider the 'body' as having involved identifiers)
        recurse_on = {
            # stmt
            ast.FunctionDef: ['args'],
            ast.ClassDef: ['bases'],

            ast.Delete: ['targets'],
            ast.Assign: ['targets', 'value'],
            ast.AugAssign: ['target', 'value'],

            ast.For: ['target', 'iter'],
            ast.While: ['test'],
            ast.If: ['test'],
            ast.With: ['items'],

            ast.Assert: ['test', 'msg'],

            ast.Import: ['names'],
            ast.ImportFrom: ['names'],

            ast.Expr: ['value'],

            # expr
            ast.BoolOp: ['values'],
            ast.BinOp: ['left', 'right'],
            ast.UnaryOp: ['operand'],
            ast.Lambda: ['args'],
            ast.IfExp: ['test'],
            ast.Dict: ['keys', 'values'],
            ast.Set: ['elts'],
            ast.ListComp: ['generators'],
            ast.SetComp: ['generators'],
            ast.DictComp: ['generators'],
            ast.GeneratorExp: ['generators'],

            ast.Yield: ['value'],
            ast.YieldFrom: ['value'],

            ast.Compare: ['left', 'comparators'],
            ast.Call: ['func', 'args', 'keywords', 'starargs', 'kwargs'],

            ast.Attribute: ['value'],
            ast.Subscript: ['value', 'slice'],
            ast.Starred: ['value'],
            ast.List: ['elts'],
            ast.Tuple: ['elts'],

            # slice
            ast.Slice: ['lower', 'upper', 'step'],
            ast.ExtSlice: ['dims'],
            ast.Index: ['value'],

            # comprehension
            ast.comprehension: ['target', 'iter', 'ifs'],

            # arguments, arg, keyword
            ast.arguments: ['args', 'vararg', 'kwonlyargs', 'kw_defaults',
                            'kwarg', 'defaults'],
            ast.arg: ['annotation'],
            ast.keyword: ['value'],

            # withitem
            ast.withitem: ['context_expr', 'optional_vars'],
        }

        # if we don't have anything to recurse on, we're done
        if type(node) not in recurse_on:
            continue

        # recursively check for identifiers
        # note that some of the attrs (eg ClassDef.bases) are themselves
        # sequences; because ast seems to always use list for these, we can
        # just check for that
        for attr_name in recurse_on[type(node)]:
            attr_value = getattr(node, attr_name)

            if isinstance(attr_value, list):
                child_nodes = attr_value
            else:
                child_nodes = [attr_value]

            # certain attrs are optional; ignore them if they're None
            child_nodes = filter(None, child_nodes)

            for child_node in child_nodes:
                child_ids = involved_identifiers(child_node)
                identifiers.extend(child_ids)

    return identifiers


def value(node, suppress_exceptions=False):
    """
    Return the value of the given node.

    Value in this context means literal value.  However, not all literals are
    currently supported.  Certain literals (such as comprehensions) would
    result in complex return values and are extremely unlikely to occur in
    practice, even if theoretically possible.

    Num, Str, Bytes, NameConstant, Set, List, Tuple, and Dict are supported.

    If a literal contains a non-literal element, or a component which cannot
    otherwise be parsed, then a StaticAnalysisError will be raised.  Note that
    this is an *extremely* common situation, and so the normal use case for
    this function *will* involve suppressing exceptions.

    For example, the list [1, 2, 3, f()] cannot be parsed without exceptions,
    even though the first three elements are constant, because of the function
    call in the last position.

    Args:
      node (ast.Node): The node to return the value of.
      suppress_exceptions (bool, optional): Whether exceptions should be
          suppressed.  If True, then this method will return None if a
          value cannot be found.  Note that as mentioned above, many use cases
          will raise exceptions, and so this should usually be given as True.
          For consistency, suppress_exceptions defaults to False.

    Returns:
      The value of the node, as a Python object.

      For example, the value of an ast.Num will be an integer or float as
      appropriate, and the value of an ast.List will be a list.

    Raises:
      StaticAnalysisError: If the node, *or any subnode* (such as an element of
          a list, to any degree of nesting) has no defined value (according to
          the rules used in this function), and suppress_exceptions is False.

    """
    # note that this is not an extensive set of mappings
    # full mappings have not been provided because trying to parse
    # arbitrarily complicated expressions leads to madness (eg, functions
    # within functions)
    # nodes which cannot be parsed will be replaced with None
    node_value = partial(value, suppress_exceptions=suppress_exceptions)

    def build_sequence(tpe):
        return lambda node: tpe(map(node_value, node.elts))

    def build_dict(node):
        keys = map(node_value, node.keys)
        values = map(node_value, node.values)
        return dict(zip(keys, values))

    mappings = {
        ast.Num: attrgetter('n'),
        ast.Str: attrgetter('s'),
        ast.Bytes: attrgetter('s'),
        ast.NameConstant: attrgetter('value'),  # None, False, True

        ast.Set: build_sequence(set),
        ast.List: build_sequence(list),
        ast.Tuple: build_sequence(tuple),

        ast.Dict: build_dict,
    }

    if type(node) in mappings:
        return mappings[type(node)](node)

    if suppress_exceptions:
        return None

    raise StaticAnalysisError(
        'No known value exists for node {}'.format(node)
    )


def identifier_or_value(node):
    nid = identifier(node, suppress_exceptions=True)
    if nid is not None:
        return nid

    val = value(node, suppress_exceptions=True)
    if val is not None:
        return val

    return None  # just default to returning None
