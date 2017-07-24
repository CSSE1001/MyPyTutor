import math
epsilon = 1e-5


class Point(object):
    """A 2D point in the cartesian plane"""
    def __init__(self, x, y):
        """
        Construct a point object given the x and y coordinates

        Parameters:
            x (float): x coordinate in the 2D cartesian plane
            y (float): y coordinate in the 2D cartesian plane
        """

        self._x = x
        self._y = y

    def __repr__(self):
        return 'Point({}, {})'.format(self._x, self._y)
