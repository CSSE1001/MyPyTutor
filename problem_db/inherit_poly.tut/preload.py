class Shape():
    """
    A representation of a shape.

    """
    def __init__(self, origin=(0, 0)):
        """Constructs a shape object
        
        Parameters:
            origin(tuple<int, int>): origin of the shape 
        """

        self.origin = origin

    def area(self):
        """
        (int) Return the area of the shape.

        """
        raise NotImplementedError()

    def vertices(self):
        """
        Return the vertices of the shape.

        Returns:
          list<tuple<int, int>>: The vertices of the shape, as a list of tuples 
          representing two dimensional points. 
          This list may be returned in any order.
        """
        raise NotImplementedError()


class Square(Shape):
    """A Square object"""
    def __init__(self, side_length, origin=(0, 0)):
        """
        Constructs a square object
        
        Parameters:
            side_length (int): Length of the sides of the square
            origin (tuple<int, int>): Coordinate of topleft corner of square
            
        """
        super().__init__(origin=origin)

        self.side_length = side_length

    def area(self):
        """
        (int) Return the area of the shape.
        """
        return self.side_length * self.side_length

    def vertices(self):
        """
        Return the vertices of the shape.

        Returns:
          list<tuple<int, int>>: The vertices of the shape, as a list of tuples 
          representing two dimensional points. 
          This list may be returned in any order.
        """
        x, y = self.origin

        return [
            (x, y),
            (x, y + self.side_length),
            (x + self.side_length, y + self.side_length),
            (x + self.side_length, y),
        ]


def total_area(shapes):
    """
    Return the total area of the given list of shapes.

    Parameters:
      shapes (list<Shape>): The list of shapes to sum the area for.

    Returns:
      int: The total area of the list of shapes, being the sum of the area of 
      each individual shape.

    """
    area = 0.

    for shape in shapes:
        area += shape.area()

    return area


def outer_bounds(shapes):
    """
    Return the outer bounds of the given list of shapes.

    Parameters:
      shapes (list<Shape>): The list of shapes to return the outer bounds for.

    Returns:
      tuple<tuple<int, int>, tuple<int, int>>: 

      The first element of the tuple is the top-left corner of a rectangle
      which could enclose every shape in the given list.
      The second element of the tuple is the bottom-right corner of that same
      rectangle.

      The top-left corner of the rectangle will be, at minimum, (0, 0).

    """
    vertices = []

    for shape in shapes:
        for vertex in shape.vertices():
            vertices.append(vertex)

    top_left_x = 0
    top_left_y = 0
    bottom_right_x = 0
    bottom_right_y = 0

    for x, y in vertices:
        if x < top_left_x:
            top_left_x = x
        elif x > bottom_right_x:
            bottom_right_x = x

        if y < top_left_y:
            top_left_y = y
        elif y > bottom_right_y:
            bottom_right_y = y

    return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)


# example usage
# note that total_area doesn't know nor care that we used instances of Square
shapes = [Square(2), Square(4, origin=(2, 2))]
area = total_area(shapes)
