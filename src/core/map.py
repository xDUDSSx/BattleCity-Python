from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from core.game import Game

from typing import Union

import numpy as np
import pyglet as pyg

from core import constants
from core import utils
from core.entities.entity import Entity
from core.entities.map.bush import Bush
from core.entities.map.destructible_wall import DestructibleWall
from core.entities.map.flag import Flag
from core.entities.map.wall import Wall
from core.entities.map.collider import Collider
from core.entities.tank.player import Player


class Map:
    """
    Holds organised information about the entities making up the world.
    Also is responsible for parsing a stage file and creating other entities based on it.

    Note: In self.map array, entities can be accessed with map[x, y] despite the the fact the numpy
    arrays are indexed [row, column]. This means the array itself doesn't look like the map on screen.
    Map slicing is inclusive from the BOTTOM_LEFT corner instead of TOP_LEFT.
    """

    def __init__(self):
        self.map: np.ndarray = None
        self.map_data: dict = None

    def generate_map_from_map_data(self, map_data: dict, game: Game) -> None:
        self.clear()
        self.map = np.empty(shape=(map_data["width"], map_data["height"]), dtype=object)
        self.map_data = map_data

        for y in range(0, self.map.shape[1]):
            for x in range(0, self.map.shape[0]):
                map_symbol = map_data["lines"][map_data['height'] - y - 1][x]
                self._parse_map_symbol(map_symbol, x, y, game)

        self._create_bounds_colliders(map_data, game)

    def _create_bounds_colliders(self, map_data: dict, game: Game) -> None:
        """
        Creates collider entities around the map to function as map boundaries.
        """
        game.entity_manager.add_entity(Collider(-constants.TILE_SIZE, 0,
                                                constants.TILE_SIZE, map_data["pixel_height"]))
        game.entity_manager.add_entity(Collider(0, -constants.TILE_SIZE,
                                                map_data["pixel_width"], constants.TILE_SIZE))
        game.entity_manager.add_entity(Collider(map_data["pixel_width"], 0,
                                                constants.TILE_SIZE, map_data["pixel_height"]))
        game.entity_manager.add_entity(Collider(0, map_data["pixel_height"],
                                                map_data["pixel_width"], constants.TILE_SIZE))

    def clear(self) -> None:
        """
        Disposes of current entities
        """
        if self.map is not None:
            for y in range(0, self.map.shape[1]):
                for x in range(0, self.map.shape[0]):
                    if self.map[x, y] is not None:
                        self.map[x, y].delete()

    def _parse_map_symbol(self, symbol: str, x: int, y: int, game: Game) -> None:
        """
        Creates entities corresponding to the symbol.
        """
        if symbol == "#":  # Destructible wall
            tile = DestructibleWall(x=x * constants.TILE_SIZE,
                                    y=y * constants.TILE_SIZE,
                                    batch=game.background_batch)
            self.map[x, y] = tile

        if symbol == "$":  # Indestructible wall
            tile = Wall(x=x * constants.TILE_SIZE,
                        y=y * constants.TILE_SIZE,
                        batch=game.background_batch)
            self.map[x, y] = tile

        if symbol == "+":  # Bush
            tile = Bush(x=x * constants.TILE_SIZE,
                        y=y * constants.TILE_SIZE,
                        batch=game.foreground_batch)
            self.map[x, y] = tile

        if symbol == "F":  # The flag
            tile = Flag(x=x * constants.TILE_SIZE,
                        y=y * constants.TILE_SIZE,
                        batch=game.batch)
            self.map[x, y] = tile
            game.game_director.flag = tile

        if symbol == "P":  # The player (not saved into the map array)
            player = Player(x=x // 2 * constants.TANK_SIZE + constants.TANK_SIZE // 2,
                            y=y // 2 * constants.TANK_SIZE + constants.TANK_SIZE // 2,
                            batch=game.batch)
            game.entity_manager.add_entity(game.register_player(player))
            game.game_director.player = player
            game.game_director.player_spawn_point = (x, y)

        else:
            pass

    def render_entity_debug_boxes(self):
        map_list = self.map.ravel()
        for obj in map_list:
            if obj is not None and hasattr(obj, "rect"):
                x = obj.rect.x
                y = obj.rect.y
                w = obj.rect.width
                h = obj.rect.height

                pyg.gl.glColor3f(1.0, 1.0, 1.0)
                pyg.graphics.draw(4, pyg.gl.GL_LINE_LOOP, ('v2f',
                                                           [x, y,
                                                            x + w, y,
                                                            x + w, y + h,
                                                            x, y + h]))

    def remove_tile(self, tile: Entity) -> None:
        """
        Removes a tile from the maps data array.
        Note that the tile is removed based on its position.
        If an entity that is not already in the map array is passed, a different entity will be removed.
        :param tile: The tile to be remove.
        """
        coords = self.get_tile_indexes_at_coordinates(tile.rect.x, tile.rect.y)
        self.map[coords] = None

    def entity_map_position(self, entity: Entity) -> Union[tuple, None]:
        """
        Retrieves map tile indexes based on entity coordinates.
        """
        return self.get_tile_indexes_at_coordinates(entity.rect.x, entity.rect.y)

    def entity_map_position_aligned_with_tiles(self, entity: Entity, aprox: int = -1):
        """
        Checks whether the entity is perfectly aligned with tile coordinates. Meaning its bottom left corner
        has the same coordinates as some tile in the map.
        :param entity:
        :return:
        """
        if aprox != -1:
            return ((entity.rect.x % constants.TILE_SIZE >= constants.TILE_SIZE - aprox or
                    entity.rect.x % constants.TILE_SIZE <= aprox) and
                   (entity.rect.y % constants.TILE_SIZE >= constants.TILE_SIZE - aprox or
                    entity.rect.y % constants.TILE_SIZE <= aprox))
        return entity.rect.x % constants.TILE_SIZE == 0 and entity.rect.y % constants.TILE_SIZE == 0

    def get_tile_at_coordinates(self, x: int, y: int, check_bounds: bool = False) -> Union[object, None]:
        """
        Returns object located at the specified world coordinates in the map.
        :return: The object instance or None
        :raises IndexError on out of bounds if check_bounds is True
        """
        if x < 0 or y < 0 or x >= self.map_data["pixel_width"] or y >= self.map_data["pixel_height"]:
            if check_bounds:
                raise IndexError("Out of bounds!")
            return None
        return self.map[x // constants.TILE_SIZE, y // constants.TILE_SIZE]

    def get_tile_indexes_at_coordinates(self, x: int, y: int, check_bounds: bool = False) -> Union[tuple, None]:
        """
        Returns indexes of the tile located at the specified world coordinates in the map.
        The tile object itself can be then accessed directly from the map array.
        :return: A tuple with the indexes or None (indexes are returned as (x, y))
        :raises IndexError on out of bounds if check_bounds is True
        """
        if x < 0 or y < 0 or x >= self.map_data["pixel_width"] or y >= self.map_data["pixel_height"]:
            if check_bounds:
                raise IndexError("Out of bounds!")
            return None
        return x // constants.TILE_SIZE, y // constants.TILE_SIZE

    def get_tile_at_indexes(self, x: int, y: int, check_bounds: bool = False) -> Union[object, None]:
        """
        Returns object located at the specified map array indexes.
        :return: The object instance or None
        :raises IndexError on out of bounds if check_bounds is True
        """
        if x < 0 or y < 0 or x >= self.map_data["width"] or y >= self.map_data["height"]:
            if check_bounds:
                raise IndexError("Out of bounds!")
            return None
        return self.map[x, y]

    def get_tile_next_to_entity(self, tile: Entity, direction: tuple, full_tile: bool = False,
                                check_bounds: bool = False) -> Union[Entity, List[Entity], None]:
        """
        Returns a tile that is next to a specified entity in a certain direction.
        Direction specifies a vector relative to the original tile pointing to the target tile.
        If the direction is one of 4 major directions and full_tile is True, a list containing 2 tiles will be returned.
        :param tile: The original tile.
        :param direction: The direction relative to the original tile.
        :param full_tile: Work with bigger tiles made out of 4. A list with 2 tiles will be returned.
        :return: Desired tile entity or None
        :raises ValueError or IndexError on out of bounds if check_bounds is True
        """
        entity_pos = self.entity_map_position(tile)
        if entity_pos is None:
            raise IndexError("Entity has an invalid map position!")
        return self.get_tile_next_to_indexes(entity_pos, direction, full_tile, check_bounds)

    def get_tile_next_to_indexes(self, entity_pos: tuple, direction: tuple, full_tile: bool = False,
                                 check_bounds: bool = False) -> Union[Entity, List[Entity], None]:
        """
        Returns a tile that is next to a specified tile in a certain direction.
        Direction specifies a vector relative to the original tile pointing to the target tile.
        If the direction is one of 4 major directions and full_tile is True, a list containing 2 tiles will be returned.
        :param entity_pos: Indexes of the original tile
        :param direction: The direction relative to the original tile.
        :param full_tile: Work with bigger tiles made out of 4. A list with 2 tiles will be returned.
        :return: Desired tile entity or None
        :raises ValueError or IndexError on out of bounds if check_bounds is True
        """
        switcher = {
            (0, 1): (1, 0),
            (0, -1): (1, 0),
            (1, 0): (0, 1),
            (-1, 0): (0, 1)
        }
        major_direction = direction in switcher
        if major_direction:
            second_tile_offset = switcher[direction]

        if full_tile:
            if direction[0] > 0:
                direction = (direction[0] + 1, direction[1])
            if direction[1] > 0:
                direction = (direction[0], direction[1] + 1)

        other_pos = utils.sum_tuples_elements(entity_pos, direction)
        target_tile = self.get_tile_at_indexes(other_pos[0], other_pos[1], check_bounds=check_bounds)

        if major_direction and full_tile:
            other_pos = utils.sum_tuples_elements(other_pos, second_tile_offset)
            second_target_tile = self.get_tile_at_indexes(other_pos[0], other_pos[1], check_bounds=check_bounds)
            return [target_tile, second_target_tile]
        else:
            return target_tile

    def get_tiles_around_tile(self, pos: tuple, radius: int, full_tile: bool = False) -> np.array:
        """
        Returns a 2D numpy array containing a square slice of the map centered on the tile at the specified
        position. The width of the slice is range*2 + 1.
        :param pos: Position of the center tile.
        :param radius: "Radius" of the square. (How many tiles to the left and right)
        :param full_tile: Work with bigger tiles made out of 4. The pos parameter should then
        represent the lower-left tile of a bigger tile. This essentially centers the final square around an
        entity that is 2 tiles wide.
        :return: A 2D numpy array
        """
        if pos is None:
            raise ValueError("Position parameter is invalid.")

        if full_tile:
            radius = radius * 2

        start_x = pos[0] - radius
        end_x = pos[0] + radius + 1
        start_y = pos[1] - radius
        end_y = pos[1] + radius + 1

        if start_x < 0:
            start_x = 0
        if end_x < 0:
            end_x = 0
        if start_y < 0:
            start_y = 0
        if end_y < 0:
            end_y = 0

        if full_tile:
            return self.map[start_x:end_x + 1, start_y:end_y + 1]

        return self.map[start_x:end_x, start_y:end_y]

    def get_tile_ray(self, pos: tuple, direction: tuple, length: int, full_tile: bool = False, return_tuples = False) -> np.array:
        """
        Returns a "ray" of tiles originating from the tile at the passed position. The starting tile IS NOT included.

        Example of ray facing right:
        O = tile at pos, # = returned tiles

        full_tile = False, length = 4

        .......
        ...O####
        ........

        full_tile = True, length = 1

        .....##.
        ...O.##.
        ........

        :param pos: Position of the ray origin tile.
        :param direction: Direction of the ray. (1,0) or (-1,0) or (0,1) or (0,-1)
        :param length: Length of the ray.
        :param full_tile: Work with bigger tiles made out of 4. Tile at pos then represents the bottom left tile.
        :param return_tuples:
        :return: A 1D (full_tile=False) or 2D numpy array containing a list of tile entities (or None references or
        tuples containing coordinate indexes if return_tuples is set to True)
        in ascending order based on position outwards from the starting position.
        The 2D array will always have 2 columns and should be iterated by rows.
        """
        if pos is None:
            return np.zeros((1, 1), dtype=object)

        if full_tile:
            length = length * 2

        if direction == (-1, 0):
            if full_tile:
                return np.flip(self.map[max(0, pos[0] - length):pos[0], pos[1]:pos[1]+2], 0)
            else:
                return np.flip(self.map[max(0, pos[0] - length):pos[0], pos[1]], 0)
        if direction == (1, 0):
            if full_tile:
                return self.map[pos[0]+2:pos[0] + length + 1, pos[1]:pos[1]+2]
            else:
                return self.map[pos[0]+1:pos[0] + length + 1, pos[1]]
        if direction == (0, 1):
            if full_tile:
                array = self.map[pos[0]:pos[0]+2, pos[1]+2:(pos[1] + length + 1)]
                return np.stack((array[0, 0:], array[1, 0:]), axis=1)
            else:
                return self.map[pos[0], pos[1]+1:(pos[1] + length + 1)]
        if direction == (0, -1):
            if full_tile:
                array = np.flip(self.map[pos[0]:pos[0]+2, max(0, pos[1] - length):pos[1]], 1)
                return np.stack((array[0, 0:], array[1, 0:]), axis=1)
            else:
                return np.flip(self.map[pos[0], max(0, pos[1] - length):pos[1]], 0)