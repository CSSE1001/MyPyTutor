from collections.abc import Sequence


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
