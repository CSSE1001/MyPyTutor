# This is all from the argparse course code
class _AttributeHolder():
    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            arg_strings.append('%s=%r'%(name, value))
        return '%s(%s)'%(type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    def _get_args(self):
        return []


class Namespace(_AttributeHolder):
    """
    Recursively transforms a set of keyword arguments into accessible
    attributes (which behaves similarly to a python module).

    """
    def __init__(self, **kwargs):
        for name, val in kwargs.items():
            setattr(self, name, val)

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = Namespace(**value)

        object.__setattr__(self, name, value)

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __contains__(self, key):
        return key in self.__dict__

    def __iter__(self):
        return iter(self.__dict__.items())
