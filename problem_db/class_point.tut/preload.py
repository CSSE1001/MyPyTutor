import math
epsilon = 1e-5


class Point(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __repr__(self):
        return 'Point({}, {})'.format(self._x, self._y)