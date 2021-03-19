import os

import pytest

from core import constants
from core.entities.map.bush import Bush
from core.entities.map.destructible_wall import DestructibleWall
from core.entities.map.flag import Flag
from core.entities.map.wall import Wall
from core.entities import map
from core.entities.tank.tank import Tank
from core.game import Game
from core.stage import Stage
from core.tests import t_utils

test1 = """############################
############################
##          ####          ##
##          ####          ##
##          +#####        ##
##           #####        ##
##  $$ +$$      ###$      ##
##  $$ X$   X   ###$      ##
##  ##  ##      ++++      ##
##  ##  ##      ++++      ##
##  #    #   #######$$    ##
##  #    #   #######$$    ##
##  #    #          ##    ##
##  #    #          ##    ##
##  ##  ##    1     ##    ##
##  ##  ##          ##    ##
##  ##  ##          ##    ##
##  ##  ##          ##    ##
##  $$  $$          ##    ##
##  $$  $$          ##    ##
##           ++           ##
##         +++++          ##
##  ##################++++##
##  ##################++++##
##                    ++++##
##            ####    ++++##
##            #  #    ++++##
##    P       #F #    ++++##"""

test2 = """                         X
                         X
$$$$$$$$$$$$  $$$$$$$$$$$$
  ##  ##  ##  ##  ##  ## X
  ##  ##  ##  ##  ##  ## X
  ##  ##  ##  ##  ##  ## X
  ##  ##  ##  ##  ##  ## X
P ##  ##############  ## X
############  ############
############F ############"""

working_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + os.pardir
game = Game(working_dir, True)


@pytest.fixture
def map1():
    map_data = Stage.generate_map_data(test1.splitlines())
    game.game_map.generate_map_from_map_data(map_data, game)

@pytest.fixture
def map2():
    map_data = Stage.generate_map_data(test2.splitlines())
    game.game_map.generate_map_from_map_data(map_data, game)


def test_generation(map1):
    assert isinstance(game.game_map.map[0, 0], DestructibleWall)
    assert isinstance(game.game_map.map[15, 0], Flag)
    assert isinstance(game.game_map.map[22, 5], Bush)
    assert game.game_map.map[14, 15] is None
    assert isinstance(game.game_map.map[14, 16], DestructibleWall)
    assert isinstance(game.game_map.map[14, 17], DestructibleWall)
    assert game.game_map.map[14, 18] is None
    assert isinstance(game.game_map.map[4, 20], Wall)
    assert isinstance(game.game_map.map[7, 21], Bush)


def test_tile_getters(map1):
    assert isinstance(game.game_map.get_tile_at_indexes(0, 0), DestructibleWall)
    assert isinstance(game.game_map.get_tile_at_indexes(15, 0), Flag)
    assert isinstance(game.game_map.get_tile_at_indexes(22, 5), Bush)
    assert game.game_map.get_tile_at_indexes(14, 15) is None
    assert isinstance(game.game_map.get_tile_at_indexes(14, 16), DestructibleWall)
    assert isinstance(game.game_map.get_tile_at_indexes(14, 17), DestructibleWall)
    assert game.game_map.get_tile_at_indexes(14, 18) is None
    assert isinstance(game.game_map.get_tile_at_indexes(4, 20), Wall)
    assert isinstance(game.game_map.map[7, 21], map.bush.Bush)

    assert isinstance(game.game_map.get_tile_at_coordinates(0, 0), DestructibleWall)
    assert isinstance(game.game_map.get_tile_at_coordinates(15 * constants.TILE_SIZE + constants.TILE_SIZE // 2,
                                                            constants.TILE_SIZE // 2), Flag)
    assert isinstance(game.game_map.get_tile_at_coordinates(22 * constants.TILE_SIZE, 5 * constants.TILE_SIZE), Bush)
    assert game.game_map.get_tile_at_coordinates(14 * constants.TILE_SIZE, 15 * constants.TILE_SIZE) is None
    assert isinstance(game.game_map.get_tile_at_coordinates(14 * constants.TILE_SIZE, 16 * constants.TILE_SIZE),
                      DestructibleWall)
    assert isinstance(game.game_map.get_tile_at_coordinates(14 * constants.TILE_SIZE, 17 * constants.TILE_SIZE),
                      DestructibleWall)
    assert game.game_map.get_tile_at_coordinates(14 * constants.TILE_SIZE, 18 * constants.TILE_SIZE) is None
    assert isinstance(game.game_map.get_tile_at_coordinates(4 * constants.TILE_SIZE, 20 * constants.TILE_SIZE), Wall)
    assert isinstance(game.game_map.get_tile_at_coordinates(7 * constants.TILE_SIZE, 21 * constants.TILE_SIZE), Bush)


def test_get_tile_ray(map1):
    pos = (12, 20)

    tiles = game.game_map.get_tile_ray(pos, (-1, 0), 4)
    assert tiles.ndim == 1 and tiles.size == 4
    t_utils.check_list_contains_objects_of_type(tiles, 1, Wall)
    assert tiles[0] is None
    assert type(tiles[3]) is Wall

    tiles = game.game_map.get_tile_ray(pos, (1, 0), 7)
    assert tiles.ndim == 1 and tiles.size == 7
    t_utils.check_list_contains_objects_of_type(tiles, 3, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles, 1, Wall)
    assert tiles[0] is None
    assert type(tiles[3]) is DestructibleWall
    assert type(tiles[6]) is Wall

    tiles = game.game_map.get_tile_ray(pos, (0, 1), 4)
    assert tiles.ndim == 1 and tiles.size == 4
    t_utils.check_list_contains_objects_of_type(tiles, 1, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles, 1, Bush)
    assert tiles[0] is None
    assert type(tiles[2]) is Bush

    tiles = game.game_map.get_tile_ray(pos, (0, -1), 15)
    assert tiles.ndim == 1 and tiles.size == 15
    t_utils.check_list_contains_objects_of_type(tiles, 1, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles, 1, Bush)
    assert tiles[0] is None
    assert type(tiles[13]) is Bush
    assert type(tiles[14]) is DestructibleWall


def test_get_tile_ray_full_tile(map1):
    pos = (12, 20)

    tiles = game.game_map.get_tile_ray(pos, (-1, 0), 4, True)
    assert tiles.shape[1] == 2 and tiles.ndim == 2 and tiles.size == 16
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 7, Wall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 1, Bush)
    t_utils.check_list_contains_objects_of_type(tiles[0], 2, None)
    t_utils.check_list_contains_objects_of_type(tiles[7], 2, Wall)

    tiles = game.game_map.get_tile_ray(pos, (1, 0), 12, True)
    assert tiles.shape[1] == 2 and tiles.ndim == 2 and tiles.size == 28
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 10, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 2, Wall)
    t_utils.check_list_contains_objects_of_type(tiles[0], 2, None)
    t_utils.check_list_contains_objects_of_type(tiles[2], 2, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles[11], 2, None)

    tiles = game.game_map.get_tile_ray(pos, (0, 1), 4, True)
    assert tiles.shape[1] == 2 and tiles.ndim == 2 and tiles.size == 12
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 10, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 1, Bush)
    t_utils.check_list_contains_objects_of_type(tiles[0], 1, None)
    t_utils.check_list_contains_objects_of_type(tiles[0], 1, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles[1], 1, Bush)
    t_utils.check_list_contains_objects_of_type(tiles[1], 1, DestructibleWall)

    tiles = game.game_map.get_tile_ray(pos, (0, -1), 7, True)
    assert tiles.shape[1] == 2 and tiles.ndim == 2 and tiles.size == 7 * 4
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 2, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 3, Bush)
    t_utils.check_list_contains_objects_of_type(tiles[0], 2, None)
    t_utils.check_list_contains_objects_of_type(tiles[2], 1, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles[13], 2, Bush)

def test_get_tile_ray_full_tile_edge_case(map2):
    pos = (12, 5)

    tiles = game.game_map.get_tile_ray(pos, (0, -1), 3, True)
    assert tiles.shape[1] == 2 and tiles.ndim == 2 and tiles.size == 10
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 2, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 1, Flag)
    t_utils.check_list_contains_objects_of_type(tiles[0], 2, None)


def test_get_tiles_around_tile(map1):
    pos = (20, 20)

    tiles = game.game_map.get_tiles_around_tile(pos, 3)
    assert tiles.ndim == 2 and tiles.size == 7 * 7
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 9, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 6, Bush)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 4, Wall)


def test_get_tiles_around_tile_full_tile(map1):
    pos = (20, 20)

    tiles = game.game_map.get_tiles_around_tile(pos, 3, True)
    assert tiles.ndim == 2 and tiles.size == 14 * 14
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 86, DestructibleWall)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 8, Bush)
    t_utils.check_list_contains_objects_of_type(tiles.ravel(), 6, Wall)


def test_get_tile_relative_to_indexes(map1):
    pos = (7, 20)
    assert type(game.game_map.get_tile_next_to_indexes(pos, (0, 1))) == Bush
    assert type(game.game_map.get_tile_next_to_indexes(pos, (1, 0))) == Wall
    assert game.game_map.get_tile_next_to_indexes(pos, (0, -1)) is None
    assert game.game_map.get_tile_next_to_indexes(pos, (-1, 0)) is None
    assert type(game.game_map.get_tile_next_to_indexes(pos, (8, -20))) == Flag


def test_get_tile_relative_to_indexes_full_tile(map1):
    pos = (7, 20)
    returned_tiles = game.game_map.get_tile_next_to_indexes(pos, (0, 1), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 2, None)

    returned_tiles = game.game_map.get_tile_next_to_indexes(pos, (1, 0), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, None)
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, Wall)

    returned_tiles = game.game_map.get_tile_next_to_indexes(pos, (0, -1), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, None)
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, DestructibleWall)

    returned_tiles = game.game_map.get_tile_next_to_indexes(pos, (-1, 0), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 2, None)


def test_get_tile_relative_to_entity(map1):
    tile = game.game_map.get_tile_at_indexes(8, 20)
    assert type(game.game_map.get_tile_next_to_entity(tile, (0, 1))) == Wall
    assert game.game_map.get_tile_next_to_entity(tile, (1, 0)) is None
    assert type(game.game_map.get_tile_next_to_entity(tile, (0, -1))) == DestructibleWall
    assert game.game_map.get_tile_next_to_entity(tile, (-1, 0)) is None
    assert type(game.game_map.get_tile_next_to_entity(tile, (7, -20))) == Flag


def test_get_tile_relative_to_entity_full_tile(map1):
    entity = Tank(x=7 * constants.TILE_SIZE + constants.TANK_SIZE // 2,
                  y=20 * constants.TILE_SIZE + constants.TANK_SIZE // 2,
                  batch=None)

    returned_tiles = game.game_map.get_tile_next_to_entity(entity, (0, 1), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 2, None)

    returned_tiles = game.game_map.get_tile_next_to_entity(entity, (1, 0), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, None)
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, Wall)

    returned_tiles = game.game_map.get_tile_next_to_entity(entity, (0, -1), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, None)
    t_utils.check_list_contains_objects_of_type(returned_tiles, 1, DestructibleWall)

    returned_tiles = game.game_map.get_tile_next_to_entity(entity, (-1, 0), True)
    assert len(returned_tiles) == 2
    t_utils.check_list_contains_objects_of_type(returned_tiles, 2, None)
