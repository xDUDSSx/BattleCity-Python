import os
from pyglet.shapes import Rectangle

from core import collision, constants
from core import utils
from core.entities.map.flag import Flag
from core.entities.map.wall import Wall
from core.entities.tank.tank import Tank
from core.game import Game
from core.entities import map
from core.stage import Stage
from core.tests import t_utils

test1 = """    #
 $  #
 $+ #
 $  #
  F #"""

working_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + os.pardir
game = Game(working_dir, True)

map_data = Stage.generate_map_data(test1.splitlines())
game.game_map.generate_map_from_map_data(map_data, game)


def test_aabb():
    assert collision.aabb(Rectangle(0, 0, 10, 10), Rectangle(10, 0, 10, 20)) is False
    assert collision.aabb(Rectangle(-20, -10, 10, 10), Rectangle(40, -5, 10, 20)) is False
    assert collision.aabb(Rectangle(40, -5, 10, 20), Rectangle(-20, -10, 10, 10)) is False

    assert collision.aabb(Rectangle(10, 20, 25, 25), Rectangle(-30, 0, 40, 20)) is False
    assert collision.aabb(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 20)) is False
    assert collision.aabb(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 21)) is True
    assert collision.aabb(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 26)) is True

    assert collision.aabb(Rectangle(50, 50, 50, 50), Rectangle(49, 50, 50, 50)) is True
    assert collision.aabb(Rectangle(0, 50, 50, 50), Rectangle(49, 50, 50, 50)) is True
    assert collision.aabb(Rectangle(20, 30, 15, 20), Rectangle(30, 35, 10, 20)) is True


def test_aabb_with_result():
    result = Rectangle(0, 0, 0, 0)

    assert utils.rect_equal(Rectangle(1, 2, 30, 30), Rectangle(1, 2, 30, 30)) is True
    assert utils.rect_equal(Rectangle(1, 2, 30, 31), Rectangle(1, 2, 30, 30)) is False

    assert collision.aabb_with_result(Rectangle(0, 0, 10, 10), Rectangle(10, 0, 10, 20), result) is False
    assert utils.rect_empty(result) is True

    assert collision.aabb_with_result(Rectangle(-20, -10, 10, 10), Rectangle(40, -5, 10, 20), result) is False
    assert collision.aabb_with_result(Rectangle(40, -5, 10, 20), Rectangle(-20, -10, 10, 10), result) is False

    assert collision.aabb_with_result(Rectangle(10, 20, 25, 25), Rectangle(-30, 0, 40, 20), result) is False
    assert collision.aabb_with_result(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 20), result) is False
    assert collision.aabb_with_result(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 21), result) is True
    assert utils.rect_equal(result, Rectangle(9, 20, 1, 1)) is True

    assert collision.aabb_with_result(Rectangle(9, 20, 25, 25), Rectangle(-30, 0, 40, 26), result) is True
    assert utils.rect_equal(result, Rectangle(9, 20, 1, 6)) is True

    assert collision.aabb_with_result(Rectangle(50, 50, 50, 50), Rectangle(49, 50, 50, 50), result) is True
    assert utils.rect_equal(result, Rectangle(50, 50, 49, 50)) is True

    assert collision.aabb_with_result(Rectangle(0, 50, 50, 50), Rectangle(49, 50, 50, 50), result) is True
    assert utils.rect_equal(result, Rectangle(49, 50, 1, 50)) is True

    assert collision.aabb_with_result(Rectangle(20, 30, 15, 20), Rectangle(30, 35, 10, 20), result) is True
    assert utils.rect_equal(result, Rectangle(30, 35, 5, 15)) is True


def test_check_collision():
    colliding_entities = []
    test_entity = Tank(x=1 * constants.TANK_SIZE + constants.TANK_SIZE // 2,
                       y=1 * constants.TANK_SIZE,
                       batch=None)
    game.entity_manager.add_entity(test_entity)

    # Basic tests
    assert collision.check_collision(test_entity, test_entity.rect, None, colliding_entities,
                                     game.entity_manager, game.game_map)
    assert len(colliding_entities) == 1
    t_utils.check_list_contains_objects_of_type(colliding_entities, 1, Flag)

    test_entity.move(-constants.TILE_SIZE // 2, 0)

    assert collision.check_collision(test_entity, test_entity.rect, None, colliding_entities,
                                     game.entity_manager, game.game_map)
    assert len(colliding_entities) == 3
    t_utils.check_list_contains_objects_of_type(colliding_entities, 1, Flag)
    t_utils.check_list_contains_objects_of_type(colliding_entities, 2, Wall)

    # With multiple entities in the entity manager
    another_test_entity = Tank(x=0 + constants.TANK_SIZE // 2,
                               y=0 + constants.TANK_SIZE // 2,
                               batch=None)
    game.entity_manager.add_entity(another_test_entity)

    assert collision.check_collision(test_entity, test_entity.rect, None, colliding_entities,
                                     game.entity_manager, game.game_map)
    assert len(colliding_entities) == 4
    t_utils.check_list_contains_objects_of_type(colliding_entities, 1, Flag)
    t_utils.check_list_contains_objects_of_type(colliding_entities, 2, Wall)
    t_utils.check_list_contains_objects_of_type(colliding_entities, 1, Tank)

    # Test ignored entities
    ignored_entities = [another_test_entity, game.game_map.get_tile_at_indexes(2, 0), game.game_map.get_tile_at_indexes(1, 1)]

    assert collision.check_collision(test_entity, test_entity.rect, ignored_entities, colliding_entities,
                                     game.entity_manager, game.game_map)
    assert len(colliding_entities) == 1
    t_utils.check_list_contains_objects_of_type(colliding_entities, 1, Wall)
