from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.map import Map
    from core.entity_manager import EntityManager

from typing import Union
import itertools
from pyglet.shapes import Rectangle

from core import utils
from core import constants
from core.entities import entity


def check_collision(calling_entity: entity.Entity, new_position: Rectangle,
                    ignored_entities: Union[list, None],
                    colliding_entities: Union[list, None],
                    entity_manager: EntityManager,
                    map: Map):
    """
    Checks whether an entities bounding box intersects any other entities.
    Entities are split into ones managed exclusively by a map and an entity_manager.
    For entities managed by a map this function attempts to only check those entities that
    are around the calling entity to improve performance.

    :param calling_entity: Entity invoking this collision check.
    :param new_position: The collision detection rectangle. Future position of an entity for example.
    :param ignored_entities: A list of entities that should be ignored in the collision detection. Can be None.
    :param colliding_entities: A list of entities that will get cleared and filled with a list of entities
    that are colliding in this calculation. Can be None.
    :param entity_manager: An entity manager for checking dynamic entities.
    :param map: Map for checking static entities.
    :return: True if a collision was detected. False otherwise.
    """
    if colliding_entities is not None:
        colliding_entities.clear()
    if ignored_entities is None:
        ignored_entities = []

    # Gathering map entities that are near the calling entity. The max distance is derived from
    # the calling entities dimensions.
    entity_max_dimension = (calling_entity.rect.width if calling_entity.rect.width > calling_entity.rect.height
                            else calling_entity.rect.height)
    if entity_max_dimension > constants.TILE_SIZE:
        necessary_check_range = entity_max_dimension // (constants.TILE_SIZE * 2)
        check_full_tile = True
    else:
        necessary_check_range = (entity_max_dimension * 2) // constants.TILE_SIZE
        check_full_tile = False

    if necessary_check_range < 1:
        necessary_check_range = 1

    entity_map_pos = map.entity_map_position(calling_entity)
    if entity_map_pos is not None:
        map_entities = map.get_tiles_around_tile(entity_map_pos, necessary_check_range, full_tile=check_full_tile)
        map_entities = map_entities.ravel()
    else:
        map_entities = []

    # Iterating through entities from both the entity_manager and those nearby in the map.
    collision_detected = False
    for other_entity in itertools.chain(map_entities, entity_manager.entities):
        if other_entity is not None and other_entity != calling_entity and other_entity.collidable:
            if other_entity not in ignored_entities:
                if aabb(other_entity.rect, new_position):
                    collision_detected = True
                    if colliding_entities is not None:
                        colliding_entities.append(other_entity)
                    else:
                        break

    return collision_detected


def aabb(a: Rectangle, b: Rectangle) -> bool:
    """
    Does Axis Aligned Bounding Box collision detection between two rectangles a and b.
    :return: True if collision between them was detected. False otherwise.
    """
    return (a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y)


def aabb_with_result(a: Rectangle, b: Rectangle, result: Rectangle) -> bool:
    """
    Does Axis Aligned Bounding Box collision detection between two rectangles a and b.
    Also calculates the intersection rectangle.
    :param a:
    :param b:
    :param result:
    :return:
    """
    # Horizontal
    amin = a.x
    amax = a.x + a.width
    bmin = b.x
    bmax = b.x + b.width
    if bmin > amin:
        amin = bmin
    result.x = amin
    if bmax < amax:
        amax = bmax
    result.width = amax - amin

    # Vertical
    amin = a.y
    amax = a.y + a.height
    bmin = b.y
    bmax = b.y + b.height
    if bmin > amin:
        amin = bmin
    result.y = amin
    if bmax < amax:
        amax = bmax
    result.height = amax - amin

    return not utils.rect_empty(result)
