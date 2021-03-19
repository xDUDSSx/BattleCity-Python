import numpy as np

from pyglet.shapes import Rectangle

from core import entities
from core import constants
from core import collision
from core import utils


class Movable(entities.entity.Entity):
    """
    An entity that can move around in the game world.
    Handles collision with other entities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = constants.MOVABLE_SPEED
        self.move_skip = constants.MOVABLE_MOVE_SKIP
        self.move_dir = np.zeros(2, int)  # Movement direction
        self.last_move = (0, 0)  # Vector of the last move, based on change of coordinates
        self.collision = True  # Whether this entity collides with other collidable entities
        self.colliding_entities = [] # Entities currently intersecting the bounding box of this one

    def logic_update(self, game, tick):
        super().logic_update(game, tick)

        last_pos = (self.rect.x, self.rect.y)

        # Collision handling and movement
        skip_move = False
        if self.move_skip != 0 and tick != -1:
            if tick % self.move_skip == 0:
                skip_move = True

        if not skip_move:
            if self.collision:
                self.resolve_collision(game, tick)
            else:
                self.move(self.move_dir[0] * self.speed, self.move_dir[1] * self.speed)

            self.last_move = (last_pos[0] - self.rect.x, last_pos[1] - self.rect.y)

    def resolve_collision(self, game, tick):
        # For speeds >1 the entity moves by multiple units.
        # To simulate how the movement would play out each 1 unit step the collision handling is executed everytime.
        # This way if an entity has a high speed it still reacts to collision as if it was moving slowly.
        for step in range(0, self.speed):
            movement_vector = np.copy(self.move_dir)

            # Collision detection (separated into 3 directions)
            diagonal_collision = False
            horizontal_collision = False
            vertical_collision = False

            new_d_pos = self.rect
            new_h_pos = self.rect
            new_v_pos = self.rect

            horizontal_colliding_entities = []
            vertical_colliding_entities = []

            if movement_vector[0] != 0 and movement_vector[1] != 0:
                utils.add_vector_to_rect(new_d_pos, movement_vector)
                diagonal_collision = collision.check_collision(self, new_d_pos,
                                                               self.colliding_entities, None,
                                                               game.entity_manager, game.game_map)
            if movement_vector[0] != 0:
                new_h_pos.x += movement_vector[0]
                horizontal_collision = collision.check_collision(self, new_h_pos,
                                                                 self.colliding_entities, horizontal_colliding_entities,
                                                                 game.entity_manager, game.game_map)
            if movement_vector[1] != 0:
                new_v_pos.y += movement_vector[1]
                vertical_collision = collision.check_collision(self, new_v_pos,
                                                               self.colliding_entities, vertical_colliding_entities,
                                                               game.entity_manager, game.game_map)

            # Wall corner evasion to improve player controls
            vertical_corner = False
            corner_entity = None
            if (len(vertical_colliding_entities) == 1 and
                    movement_vector[0] == 0 and
                    len(horizontal_colliding_entities) != 1):
                corner_entity = vertical_colliding_entities[0]
                vertical_corner = True

            if (len(horizontal_colliding_entities) == 1 and
                    movement_vector[1] == 0 and
                    len(vertical_colliding_entities) != 1):
                corner_entity = horizontal_colliding_entities[0]
                vertical_corner = False

            if corner_entity is not None:
                if isinstance(corner_entity, entities.map.wall.Wall):
                    corner_w = corner_entity.rect.width / constants.WALL_SLIDE_FACTOR
                    corner_w_remainder = corner_entity.rect.width - corner_w
                    corner_h = corner_entity.rect.height / constants.WALL_SLIDE_FACTOR
                    corner_h_remainder = corner_entity.rect.height - corner_h

                    # Corner zones
                    bottomLeftCorner = Rectangle(corner_entity.rect.x, corner_entity.rect.y,
                                                 corner_w, corner_h)
                    topLeftCorner = Rectangle(corner_entity.rect.x, corner_entity.rect.y + corner_h_remainder,
                                              corner_w, corner_h)
                    bottomRightCorner = Rectangle(corner_entity.rect.x + corner_w_remainder, corner_entity.rect.y,
                                                  corner_w, corner_h)
                    topRightCorner = Rectangle(corner_entity.rect.x + corner_w_remainder,
                                               corner_entity.rect.y + corner_h_remainder,
                                               corner_w, corner_h)

                    new_position_rect = new_v_pos if vertical_corner else new_h_pos
                    intersection_rect = Rectangle(0, 0, 0, 0)
                    if collision.aabb_with_result(new_position_rect, corner_entity.rect, intersection_rect):
                        if utils.rect_in_rect(intersection_rect, bottomLeftCorner):
                            if vertical_corner:
                                movement_vector[0] = -1
                            else:
                                movement_vector[1] = -1
                        if utils.rect_in_rect(intersection_rect, topLeftCorner):
                            if vertical_corner:
                                movement_vector[0] = -1
                            else:
                                movement_vector[1] = 1
                        if utils.rect_in_rect(intersection_rect, topRightCorner):
                            if vertical_corner:
                                movement_vector[0] = 1
                            else:
                                movement_vector[1] = 1
                        if utils.rect_in_rect(intersection_rect, bottomRightCorner):
                            if vertical_corner:
                                movement_vector[0] = 1
                            else:
                                movement_vector[1] = -1

            # Movement / Collision response
            movement_occurred = False

            if diagonal_collision and not horizontal_collision and not vertical_collision:
                self.move(movement_vector[0], 0)  # Force horizontal movement
                movement_occurred = True
            else:
                if not horizontal_collision:
                    self.move(movement_vector[0], 0)
                    movement_occurred = True
                if not vertical_collision:
                    self.move(0, movement_vector[1])
                    movement_occurred = True

            # Final collision check to update the colliding entities list.
            # TODO: Probably not necessary, should be covered by one of the initial checks
            collision.check_collision(self, self.rect, None, self.colliding_entities,
                                      game.entity_manager, game.game_map)

            if not movement_occurred:
                break

    def resolve_rotation_4_axis(self):
        """
        Aligns the sprite orientation with the movement direction in 4 axis.
        :return:
        """

        if self.move_dir[0] == 1:
            self.face("R")
        if self.move_dir[0] == -1:
            self.face("L")
        if self.move_dir[1] == 1:
            self.face("U")
        if self.move_dir[1] == -1:
            self.face("D")

    def is_moving(self) -> bool:
        """
        Determines whether this entity is currently moving based on its last_move information.
        :return: True if moving, False otherwise
        """
        return any(map(lambda x: x != 0, self.last_move))
