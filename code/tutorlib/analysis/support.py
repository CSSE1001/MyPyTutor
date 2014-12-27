from collections.abc import Sequence


class StaticAnalysisError(Exception):
    pass


class NonePaddedList(Sequence):
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
        self._data = list(iterable)

    def __repr__(self):
        return 'NonePaddedList({!r})'.format(self._data)

    def __getitem__(self, item):
        if item < len(self):
            return self._data[item]
        return None

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        # default __iter__ implementation uses try/except on successive
        # __getitem__ calls, but because we return None for invalid indices
        # we will never actually cause the exception
        # instead, make use of the fact that len(self) is defined
        for idx in range(len(self)):
            yield self[idx]
