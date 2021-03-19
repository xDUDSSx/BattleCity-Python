from __future__ import annotations
from typing import TYPE_CHECKING, List

from core.entities.particles.projectile import Projectile

if TYPE_CHECKING:
    from core.map import Map
    from core.game import Game

import random

from core import constants
from core.entities.map.flag import Flag
from core.entities.map.wall import Wall
from core.entities.tank import tank
from core.texture_manager import TextureManager


class Computer(tank.Tank):
    """
    An AI controlled tank.
    The AI is made to replicate the original BattleCity AI.
    Thankfully (in a way), the original AI seems pretty dumb so no fancy pathfinding or anything is used.

    The AI picks random directions to move in when it has no movement.
    Additionally there is a chance that it will turn at random to the sides specified by AI_JUNCTION_TURN_CHANCE

    Every turn has a bias that points the tank towards the FLAG so that the tank eventually reaches it.
    The bias is controlled by AI_FLAG_DIRECTION_BIAS.

    If there is a flag within its AI_VISION_TILE_RANGE, it stops turning.

    It shoots at random intervals, the max shoot interval is AI_SHOOT_PERIOD.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture1 = TextureManager.tank_standard_1
        self.texture2 = TextureManager.tank_standard_2
        self.image = self.texture1
        # self.color = (50, 100, 255)

        self.logic_cooldown = 0
        self.shoot_cooldown = 0

    def logic_update(self, game: Game, tick):
        if self.logic_cooldown <= 0:
            self._ai_update(game, tick)
            self.logic_cooldown = constants.AI_LOGIC_TIME_STEP
        else:
            self.logic_cooldown -= 1

        super().logic_update(game, tick)

        # self.color = (self.color[0] + 1, self.color[1] + 1, self.color[2] + 1)
        # if any(c > 255 for c in self.color):
        #     self.color = tuple(c % 255 for c in self.color)

    def _ai_update(self, game: Game, tick):
        """
        Logic update to the ai decision making.
        """
        map_pos = game.game_map.entity_map_position(self)

        flag_detected = False
        ray_tiles = game.game_map.get_tile_ray(map_pos, self.facing_direction, constants.AI_VISION_TILE_RANGE, True)
        for tiles in ray_tiles:
            for tile in tiles:
                if type(tile) is Wall:
                    break
                if isinstance(tile, Flag):
                    flag_detected = True
                    break

        if not flag_detected:
            if not self.is_moving():
                self.move_dir = self._get_random_direction(game)
            else:
                # print(f"X: {self.rect.x} Y: {self.rect.y}")
                # print(f"Aligned: {game.game_map.entity_map_position_aligned_with_tiles(self)}")
                # print(f"Junctions: {self._junction_path_count(game.game_map)}")
                if (game.game_map.entity_map_position_aligned_with_tiles(self, aprox=2) and
                        self._junction_path_count(game.game_map) > 2):
                    if random.random() < constants.AI_JUNCTION_TURN_CHANCE:
                        for i in range(0, 5):
                            random_dir = self._get_random_direction(game)
                            if random_dir[0] != self.move_dir[0] and random_dir[1] != self.move_dir[1]:
                                self.move_dir = random_dir
                                break

        self._shoot_logic(game)

    def _shoot_logic(self, game):
        if self.can_shoot() and self.shoot_cooldown <= 0:
            self.shoot(game)
            self.shoot_cooldown = random.random() * constants.AI_SHOOT_PERIOD
        else:
            self.shoot_cooldown -= 1

    def _junction_path_count(self, game_map: Map) -> int:
        """
        Counts the number of directions without obstacles.
        """
        directions = {
            0: (-1, 0),
            1: (1, 0),
            2: (0, -1),
            3: (0, 1),
        }
        path_count = 0

        for i in range(0, 4):
            direction = directions[i]

            try:
                tiles = game_map.get_tile_next_to_entity(self, direction, True, True)
            except IndexError:
                continue
            tiles_free = True
            for tile in tiles:
                if tile is not None and tile.collidable:
                    tiles_free = False
                    break
            if tiles_free:
                path_count += 1

        return path_count

    def _get_random_direction(self, game: Game) -> tuple:
        """
        Picks a random biased direction with no obstacles.
        """
        directions = {
            0: (0, 1),  # U
            1: (-1, 0),  # L
            2: (0, -1),  # D
            3: (1, 0),  # R
        }

        dir_bias = self._get_flag_biased_weights(game)

        # Find a direction where there is free space to move towards.
        for i in range(0, 100):
            direction = random.choices(directions, weights=dir_bias)[0]
            try:
                tiles = game.game_map.get_tile_next_to_entity(self, direction, True, True)
            except IndexError:
                continue
            tiles_free = True
            for tile in tiles:
                if tile is not None and tile.collidable:
                    tiles_free = False
                    break
            if tiles_free:
                break

        return direction

    def _get_flag_biased_weights(self, game: Game) -> List[float]:
        direction_biases = [1., 1., 1., 1.]  # 0 = U, 1 = L, 2 = D, 3 = R

        if game.game_director.flag.center_x() > self.center_x():
            direction_biases[3] = direction_biases[3] * constants.AI_FLAG_DIRECTION_BIAS
        else:
            direction_biases[1] = direction_biases[1] * constants.AI_FLAG_DIRECTION_BIAS

        if game.game_director.flag.center_y() > self.center_y():
            direction_biases[0] = direction_biases[0] * constants.AI_FLAG_DIRECTION_BIAS
        else:
            direction_biases[2] = direction_biases[2] * constants.AI_FLAG_DIRECTION_BIAS

        return direction_biases

    def damage(self, game, other_entity=None) -> bool:
        if isinstance(other_entity, Projectile) and other_entity.player_owned == False:
            return True
        super().damage(game, other_entity)