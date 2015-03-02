from functools import partial, wraps


def skip_if_attr(attr, val):
    def wrapper(f):
        @wraps(f)
        def method(self, *args, **kwargs):
            if getattr(self, attr) == val:
                return
            return f(self, *args, **kwargs)
        return method
    return wrapper


skip_if_attr_none = partial(skip_if_attr, val=None)