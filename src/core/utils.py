import math

from pyglet.shapes import Rectangle


def add_vector_to_rect(rectangle, vector):
    """
    Moves a rectangle by a vector.
    """
    rectangle.x += vector[0]
    rectangle.y += vector[1]


def center_rect_in_rect(center_rect: Rectangle, outer_rect: Rectangle):
    """
    Aligns a rectangle in center of another rectangle.
    """
    center_rect.x = (outer_rect.x + outer_rect.width // 2) - center_rect.width // 2
    center_rect.y = (outer_rect.y + outer_rect.height // 2) - center_rect.height // 2


def rect_empty(rect: Rectangle) -> bool:
    """
    Check for <= zero height or width of a rectangle.
    """
    return rect.width <= 0 or rect.height <= 0


def rect_equal(rect1: Rectangle, rect2: Rectangle):
    return rect1.x == rect2.x and rect1.y == rect2.y and rect1.width == rect2.width and rect1.height == rect2.height


def rect_in_rect(rect1: Rectangle, rect2: Rectangle) -> bool:
    """
    Checks whether a rectangle rect1 is fully contained within a rectangle rect2.
    """
    bottomLeft = (rect1.x, rect1.y)
    topRight = (rect1.x + rect1.width, rect1.y + rect1.height)
    return point_in_rect(bottomLeft, rect2) and point_in_rect(topRight, rect2)


def point_in_rect(point: tuple, rect: Rectangle) -> bool:
    """
    Checks if a point is located within a rectangle.
    :param point: tuple with 2 elements (x and y)
    :param rect: the rectangle
    """
    if point[0] < rect.x:
        return False
    if point[1] < rect.y:
        return False
    if point[0] > rect.x + rect.width:
        return False
    if point[1] > rect.y + rect.height:
        return False
    return True


def set_rect(rect: Rectangle, x, y, w, h):
    """
    Sets the rectangle dimensions to different ones.
    """
    rect.x = x
    rect.y = y
    rect.width = w
    rect.height = h


def get_center_of_rect(rect: Rectangle) -> tuple:
    return rect.x + rect.width // 2, rect.y + rect.height // 2


def determine_point_quadrant(point1: tuple, point2: tuple) -> int:
    """
    Determines in which quadrant point1 is in relation to point2 (as if point2 was 0,0).
    If indeterminate, bottom-left is favored.
    :return: Number 1 to 4 representing the quadrants (1 is top-right, 2 top-left)
    """
    if point1[0] <= point2[0]:
        if point1[1] <= point2[1]:
            return 3
        else:
            return 2
    else:
        if point1[1] <= point2[1]:
            return 4
        else:
            return 1


def sum_tuples_elements(t1: tuple, t2: tuple) -> tuple:
    """
    Adds two tuples element wise. The tuples must have the same size and summable element type.
    Example: (2, 1) + (4, 7) ==  (6, 8)
    :return: Summed tuple
    :raises ValueError on invalid arguments.
    """
    if t1 is None or t2 is None:
        raise ValueError("Cannot sum None!")
    if len(t1) != len(t2):
        raise ValueError("Tuples aren't the same length!")
    return tuple(map(sum, zip(t1, t2)))


def distance(p1: tuple, p2: tuple) -> float:
    return math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))


def manhattan_distance(p1: tuple, p2: tuple) -> float:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
