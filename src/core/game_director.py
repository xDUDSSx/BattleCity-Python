from __future__ import annotations
from typing import TYPE_CHECKING, List, Type

import os
import random

from core import utils, constants
from core.entities.particles.bling import Bling
from core.entities.tank.computer import Computer
from core.entities.tank.tank import Tank
from core.game_state import GameState
from core.stage import Stage
from core.entities.map.flag import Flag
from core.entities.tank.player import Player

if TYPE_CHECKING:
    from core.game import Game


class GameDirector:
    """
    Manages the gameplay itself. Enemy tank spawning, health, win/fail conditions.
    """

    def __init__(self, game: Game):
        self.game = game
        self.flag: Flag = None
        self.player: Player = None
        self.player_spawn_point = None
        self.stage: Stage = None
        self.stages: List[Stage] = None

        self.spawn_cooldown = 0
        self.spawned_tanks = []
        self.spawned_blings = []
        self.player_bling = None

    def init(self, working_dir: str):
        self.stages = Stage.load_stages(working_dir + os.sep + "stages")
        self.stage = self.stages[0]

    def reset(self):
        self.spawn_cooldown = 0
        self.spawned_tanks = []
        self.spawned_blings = []

    def update(self, game: Game):
        # Tank spawning
        self.handle_tank_spawning(game)

        # Flag destroyed
        if self.flag.destroyed:
            game.game_over(self.stage)

        # Count enemy tanks and player count
        if len(self.spawned_tanks) + len(self.spawned_blings) <= 0 and self.stage.active_tanks <= 0:
            game.stage_clear(self.stage)
        if self.player.to_remove and self.player_bling is None:
            self.stage.active_player_lives -= 1
            if self.stage.active_player_lives <= 0:
                # No player lives left, game over
                game.game_over(self.stage)
            else:
                # Respawn player
                self.player_bling = self.spawn_tank_bling(self.player_spawn_point, game)

    def handle_tank_spawning(self, game: Game) -> None:
        if (len(self.spawned_tanks) + len(self.spawned_blings) < self.stage.max_tanks_at_once
                and self.spawn_cooldown <= 0
                and self.stage.active_tanks > 0):
            self.trigger_tank_spawn(game)
        self.update_tank_spawns(game)

        if self.spawn_cooldown <= 0:
            self.spawn_cooldown = random.random() * constants.NEW_TANK_SPAWN_MAX_COOLDOWN
        self.spawn_cooldown -= 1

        if self.player_bling is not None:
            if self.player_bling.dead:
                # Respawn player
                self.player = Player(x=self.player_bling.rect.x + constants.TANK_SIZE // 2,
                                     y=self.player_bling.rect.y + constants.TANK_SIZE // 2,
                                     batch=game.batch)
                game.entity_manager.add_entity(game.register_player(self.player))
                self.player_bling = None

    def update_tank_spawns(self, game: Game):
        to_remove = []
        for bling in self.spawned_blings:
            if bling.dead:
                to_remove.append(bling)
                computer = Computer(x=bling.rect.x + constants.TANK_SIZE // 2,
                                    y=bling.rect.y + constants.TANK_SIZE // 2,
                                    batch=game.batch)
                game.entity_manager.add_entity(computer)
                self.spawned_tanks.append(computer)
        for bling in to_remove:
            self.spawned_blings.remove(bling)

        to_remove.clear()
        for tank in self.spawned_tanks:
            if tank.health <= 0:
                to_remove.append(tank)
        for tank in to_remove:
            self.spawned_tanks.remove(tank)

    def trigger_tank_spawn(self, game: Game):
        map_width = game.game_map.map_data["width"]
        map_height = game.game_map.map_data["height"]

        flag_pos = game.game_map.entity_map_position(self.flag)

        potential_spawn_points = []
        for x in (0, map_width - 2):
            for y in range(0, map_height - 1):
                potential_spawn_points.append((x, y))
        for y in (0, map_height - 2):
            for x in range(0, map_width - 1):
                potential_spawn_points.append((x, y))

        for i in range(0, 100):
            spawn_pos = random.choice(potential_spawn_points)

            if utils.manhattan_distance(flag_pos, spawn_pos) < (map_width + map_height)/2/1.8:
                continue

            tiles = []
            tile = game.game_map.get_tile_at_indexes(spawn_pos[0], spawn_pos[1])
            tiles.append(tile is None or tile.collidable == False)
            tile = game.game_map.get_tile_at_indexes(spawn_pos[0] + 1, spawn_pos[1])
            tiles.append(tile is None or tile.collidable == False)
            tile = game.game_map.get_tile_at_indexes(spawn_pos[0] + 1, spawn_pos[1] + 1)
            tiles.append(tile is None or tile.collidable == False)
            tile = game.game_map.get_tile_at_indexes(spawn_pos[0], spawn_pos[1] + 1)
            tiles.append(tile is None or tile.collidable == False)

            if not all(tiles):
                continue

            self.stage.active_tanks -= 1
            self.spawned_blings.append(self.spawn_tank_bling(spawn_pos, game))
            break

    def spawn_tank_bling(self, spawn_pos: tuple, game: Game) -> Bling:
        bling = Bling(x=spawn_pos[0] * constants.TILE_SIZE,
                      y=spawn_pos[1] * constants.TILE_SIZE,
                      batch=game.foreground_batch)
        game.entity_manager.add_entity(bling)
        return bling

    def load_stage(self, index: int, game: Game):
        self.flag = None  # Set by the map generation process
        self.player = None
        if self.stages[index] is not None:
            self.stages[index].load(self.game)
            self.stage = self.stages[index]
            self.adjust_game_window(self.stage, game)
        else:
            raise RuntimeError(f"Stage {index} failed to load!")

    def adjust_game_window(self, stage: Stage, game: Game):
        game.window.width = stage.map_data["pixel_width"] + constants.UI_SIDE_PANEL_SIZE
        game.window.height = stage.map_data["pixel_height"]