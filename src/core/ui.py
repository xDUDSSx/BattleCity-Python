from __future__ import annotations
from typing import TYPE_CHECKING

import pyglet as pyg
import numpy as np
from pyglet.sprite import Sprite

from core import constants
from core.texture_manager import TextureManager
from core.game_state import GameState

if TYPE_CHECKING:
    from core.game import Game


class UI:
    def __init__(self):
        self.batch = pyg.graphics.Batch()
        self.tank_icons = np.empty(shape=(constants.UI_TANK_ICONS_MAX_ROWS, constants.UI_TANK_ICONS_MAX_COLS),
                                   dtype=object)
        self.player_tank_icons = np.empty(shape=(constants.PLAYER_LIVES, 1), dtype=object)

    def update(self, game: Game):
        if game.game_state == GameState.GAME:
            self.draw_enemy_tanks_remaining(game)
            self.draw_player_health(game)

    def draw_player_health(self, game: Game, reset=False):
        if game.game_director.stage is None:
            return

        tank_icon_count = 0
        target_icon_count = game.game_director.stage.active_player_lives
        for row in range(0, self.player_tank_icons.shape[0]):
            for col in range(0, self.player_tank_icons.shape[1]):
                tank_icon_count += 1
                if tank_icon_count <= target_icon_count:
                    if self.player_tank_icons[row, col] is None or reset:
                        tank_icon_sprite = Sprite(img=TextureManager.tank_player_1,
                                                  x=game.game_map.map_data["pixel_width"]
                                                    + constants.UI_SIDE_PANEL_SIZE // 2,
                                                  y=(row * constants.UI_PLAYER_ICON_SIZE)
                                                    + row * constants.UI_TANK_ICONS_GAP*0.5
                                                    + constants.UI_TANK_ICONS_TOP_PAD * 1.5,
                                                  batch=self.batch)
                        tank_icon_sprite.scale = 2
                        self.player_tank_icons[row, col] = tank_icon_sprite
                else:
                    if self.player_tank_icons[row, col] is not None:
                        self.player_tank_icons[row, col].delete()
                        self.player_tank_icons[row, col] = None

    def draw_enemy_tanks_remaining(self, game: Game, reset=False):
        if game.game_director.stage is None:
            return

        tank_icon_count = 0
        target_icon_count = game.game_director.stage.active_tanks
        for row in range(0, self.tank_icons.shape[0]):
            for col in range(0, self.tank_icons.shape[1]):
                tank_icon_count += 1
                if tank_icon_count <= target_icon_count:
                    if self.tank_icons[row, col] is None or reset:
                        tank_icon_sprite = Sprite(img=TextureManager.tank_icon,
                                                  x=game.game_map.map_data["pixel_width"]
                                                    + col * constants.UI_TANK_ICON_SIZE
                                                    + col * constants.UI_TANK_ICONS_GAP
                                                    + constants.UI_SIDE_PANEL_SIZE // 2
                                                    - constants.UI_TANK_ICONS_WIDTH // 2,
                                                  y=game.game_map.map_data["pixel_height"]
                                                    - (row * constants.UI_TANK_ICON_SIZE)
                                                    - constants.UI_TANK_ICON_SIZE
                                                    - constants.UI_TANK_ICONS_TOP_PAD,
                                                  batch=self.batch)
                        tank_icon_sprite.scale = 3
                        self.tank_icons[row, col] = tank_icon_sprite
                else:
                    if self.tank_icons[row, col] is not None:
                        self.tank_icons[row, col].delete()
                        self.tank_icons[row, col] = None
