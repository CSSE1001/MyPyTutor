from collections import defaultdict
from collections.abc import Hashable, Iterable, Sequence, MutableMapping


class StaticAnalysisError(Exception):
    """
    An error encountered in static analysis.

    """
    pass


class NonePaddedList(Sequence):
    """
    A sequence which returns None instead of raising IndexError when an
    out-of-range index is requested.

    Both __len__ and __iter__ will operate as on the underlying sequence.

    """
    def __init__(self, iterable=None):
        """
        Create a new NonePaddedList object.

        Args:
          iterable (iterable, optional): The iterable to build the object from.
              This argument will be converted to a list for internal use.  Note
              that this means that passing an unordered iterable may lead to
              inconsistent results.
              Defaults to None.  If None, will be treated as an empty list.

        """
        if iterable is None:
            iterable = []
        self._data = list(iterable)

    def __repr__(self):
        return 'NonePaddedList({!r})'.format(self._data)

    def __getitem__(self, item):
        """
        Return the value at the given index, or None.

        Returns:
          iterable[item] if item is in [0, len(self)), where iterable is the
          iterable this NonePaddedList was constructed with.

          None otherwise.

        """
        if item < len(self):
            return self._data[item]
        return None

    def __len__(self):
        """
        Return the length of this NonePaddedList.

        Returns:
          The length of the iterable this NonePaddedList was constructed with.
        """
        return len(self._data)

    def __iter__(self):
        """
        Yield elements of self.

        This override is necessary because the default Sequence.__iter__
        implementation uses try/except for IndexError on successive
        Sequence.__getitem__ calls.

        Because the point of a NonePaddedList is to return None when indexed
        with an out-of-range value, this class will never actually raise
        IndexError.  The mixin implementation will therefore yield an infinite
        iterator, which is not desirable.

        Rather than directly iterating over the provided iterable, this method
        makes use of the definition of __len__.

        Yields:
          Elements of the iterable this NonePaddedList was constructed with.

        """
        for idx in range(len(self)):
            yield self[idx]


class AutoHashingDefaultDict(MutableMapping):
    """
    A MutableMapping (ie, a dict) which will use repr(key) in place of key for
    any unhashable type.

    There are so many dragons with this class that it's insane; use with
    *extreme* caution

    In particular, note that certain keys may be indistinguishable due to
    identical string representations.  (As the id of this class is prepended
    to the converted keys, however, it should be unlikely for a bare string
    to be identical to a string representation of a class.)

    """
    def __init__(self, missing_func=None, *args, **kwargs):
        self._store = defaultdict(missing_func, *args, **kwargs)

        self._key_mappings = {}

    def _convert_key(self, key):
        # originally, I had some elegant code here that was intended to handle
        # iterables as a special case and recurse
        # that approach is *not* viable, as Python objects can be self-
        # referential (thus creating a loop)
        # as is often the case, it's easier to ask forgiveness than permission
        def hashable(obj):
            try:
                hash(obj)
            except Exception:
                return False
            return True

        if not hashable(key):
            # prepend the id of this class to the repr of the key
            # this should reduce collisions with, eg, '()' or '[]'
            key = '{}.{}'.format(id(self), repr(key))
        return key

    def __str__(self):
        return str(self._store)

    def __repr__(self):
        return repr(self._store)

    def __getitem__(self, key):
        return self._store[self._convert_key(key)]

    def __setitem__(self, key, value):
        if not isinstance(key, Hashable):
            skey = self._convert_key(key)
            self._key_mappings[skey] = key
            key = skey

        self._store[key] = value

    def __delitem__(self, key):
        skey = self._convert_key(key)
        del self._store[skey]

        if skey in self._key_mappings:
            del self._key_mappings[skey]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def keys(self):
        # TODO: use KeysView?
        return (self._key_mappings.get(k, k) for k in super().keys())

    def items(self):
        # TODO: use ItemsView?
        return zip(self.keys(), self.values())
