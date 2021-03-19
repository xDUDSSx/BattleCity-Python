import pytest
from pyglet.shapes import Rectangle
from core import utils


def test_rect_functions():
    rect = Rectangle(20, -10, 20, 5)
    utils.add_vector_to_rect(rect, (6, 8))
    assert rect.x == 26 and rect.y == -2 and rect.width == 20 and rect.height == 5
    rect = Rectangle(20, -10, 20, 5)
    utils.add_vector_to_rect(rect, (-5, -13))
    assert rect.x == 15 and rect.y == -23 and rect.width == 20 and rect.height == 5
    rect = Rectangle(20, -10, 20, 5)
    utils.add_vector_to_rect(rect, (45, 100))
    assert rect.x == 65 and rect.y == 90 and rect.width == 20 and rect.height == 5

    rect = Rectangle(10, 20, 50, 50)
    rect2 = Rectangle(0, 0, 30, 30)
    utils.center_rect_in_rect(rect2, rect)
    assert rect2.x == 20 and rect2.y == 30 and rect2.width == 30 and rect2.height == 30
    assert rect.x == 10 and rect.y == 20 and rect.width == 50 and rect.height == 50

    rect = Rectangle(10, 20, 50, 50)
    rect2 = Rectangle(0, 0, 30, 30)
    utils.center_rect_in_rect(rect, rect2)
    assert rect.x == -10 and rect.y == -10 and rect.width == 50 and rect.height == 50
    assert rect2.x == 0 and rect2.y == 0 and rect2.width == 30 and rect2.height == 30

    rect = Rectangle(10, 20, 50, 50)
    rect2 = Rectangle(0, 0, 30, 30)
    assert not utils.rect_empty(rect) and not utils.rect_empty(rect2)
    assert utils.rect_empty(Rectangle(10, 10, 1, 0))
    assert utils.rect_empty(Rectangle(10, 10, -0, 5))
    assert utils.rect_empty(Rectangle(10, 10, 43, -2))
    assert utils.rect_empty(Rectangle(10, 10, 0, 0))
    assert not utils.rect_empty(Rectangle(10, 10, 1, 1))

    assert not utils.rect_equal(rect, rect2)
    rect2.x = rect.x
    rect2.y = rect.y
    assert not utils.rect_equal(rect, rect2)
    rect2.width = rect.width
    rect2.height = rect.height
    assert utils.rect_equal(rect, rect2)

    assert utils.rect_in_rect(rect, rect2)
    rect2.x += 1
    assert not utils.rect_in_rect(rect, rect2)
    rect2.height = 10
    rect2.width = 10
    assert utils.rect_in_rect(rect2, rect)

    assert utils.point_in_rect((25, 25), rect)
    assert utils.point_in_rect((rect.x, 25), rect)
    assert utils.point_in_rect((rect.x + rect.width, rect.y), rect)
    assert not utils.point_in_rect((rect.x + rect.width + 1, 25), rect)

    rect = Rectangle(0, 0, 10, 10)
    utils.set_rect(rect, 4, -2, 22, 6)
    assert rect.x == 4 and rect.y == -2 and rect.width == 22 and rect.height == 6

    assert utils.get_center_of_rect(rect) == (15, 1)


def test_determine_point_quadrant():
    assert utils.determine_point_quadrant((-5, 2), (-10, 20)) == 4
    assert utils.determine_point_quadrant((10, 20), (0, 4)) == 1
    assert utils.determine_point_quadrant((0, 20), (5, 4)) == 2
    assert utils.determine_point_quadrant((-4, -1), (5, 43)) == 3

    assert utils.determine_point_quadrant((0, 0), (0, 0)) == 3
    assert utils.determine_point_quadrant((-2, 4), (-2, 0)) == 2
    assert utils.determine_point_quadrant((-2, -5), (-2, -2)) == 3
    assert utils.determine_point_quadrant((4, -5), (2, -5)) == 4


def test_sum_tuples_elements():
    assert utils.sum_tuples_elements((1, 4), (2, 11)) == (3, 15)
    assert utils.sum_tuples_elements((-6, 20), (-8, 0)) == (-14, 20)
    assert utils.sum_tuples_elements((-10, -20), (10, 45)) == (0, 25)
    assert utils.sum_tuples_elements((0, 0), (0, 0)) == (0, 0)

    with pytest.raises(ValueError):
        assert utils.sum_tuples_elements((0, 0), None)
    with pytest.raises(ValueError):
        assert utils.sum_tuples_elements((3, 1), (-4, -5, 1))
