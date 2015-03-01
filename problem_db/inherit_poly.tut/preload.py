class Shape():
    def area(self):
        raise NotImplementedError()


class Square(Shape):
    def __init__(self, side_length):
        self.side_length = side_length

    def area(self):
        return self.side_length * self.side_length


def total_area(shapes):
    """
    Return the total area of the given list of shapes.

    Args:
      shapes ([Shape]): The list of shapes to sum the area for.

    Returns:
      The total area of the list of shapes, being the sum of the area of each
      individual shape.

    """
    area = 0.

    for shape in shapes:
        area += shape.area()

    return area