def compose(f, g):
    """
    Return the composition of f and g.

    """
    return lambda x: f(g(x))

