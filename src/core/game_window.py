from __future__ import annotations
from typing import TYPE_CHECKING

from core.game_state import GameState
from core.texture_manager import TextureManager

if TYPE_CHECKING:
    from core.game import Game

import pyglet as pyg
from pyglet.gl import *
from pyglet.window import key


class GameWindow(pyg.window.Window):
    """
    UI Window of the game. A subclass of the pyglet Window object.
    """
    def __init__(self, game: Game, *args, **kwargs):
        super().__init__(*args, resizable=False, caption="BattleTown", vsync=False, **kwargs)
        self.game = game
        self.set_icon(TextureManager.tank_icon)

        # Window background
        pyglet.gl.glClearColor(148. / 255, 153. / 255, 148. / 255, 1)

        # Texture filtering
        pyglet.image.Texture.default_min_filter = GL_NEAREST
        pyglet.image.Texture.default_mag_filter = GL_NEAREST

        # Labels
        self.main_menu_label = pyglet.text.Label('Press <ENTER> to start',
                                  font_name='Monospaced',
                                  font_size=24,
                                  x=self.width // 2, y=self.height // 2,
                                  anchor_x='center', anchor_y='center')
        self.game_finished_label = None

        # Map background
        self.map_background_rect = pyg.shapes.Rectangle(0, 0, 0, 0)
        self.map_background_rect.color = (0, 0, 0)

    def on_draw(self):
        if self.game.game_state in [GameState.GAME, GameState.GAME_OVER]:
            pyglet.gl.glClearColor(148. / 255, 153. / 255, 148. / 255, 1)
        else:
            pyglet.gl.glClearColor(0, 0, 0, 0)
        self.clear()

        if self.game.game_state in [GameState.GAME, GameState.GAME_OVER]:
            if self.game.game_map.map_data is not None:
                self.map_background_rect.width = self.game.game_map.map_data["pixel_width"]
                self.map_background_rect.height = self.game.game_map.map_data["pixel_height"]
                self.map_background_rect.draw()

            self.game.background_batch.draw()
            self.game.batch.draw()
            self.game.foreground_batch.draw()
            self.game.ui.batch.draw()

        if self.game.game_state == GameState.MAIN_MENU:
            self.main_menu_label.draw()

        if self.game.game_state == GameState.GAME_FINISHED:
            self.game_finished_label.draw()

        if self.game.draw_bounding_boxes and self.game.game_map.map_data is not None:
            self.game.game_map.render_entity_debug_boxes()
            self.game.entity_manager.render_entity_debug_boxes()

        if self.game.show_fps:
            self.game.fps_display.draw()

        # Use later for debug bounding boxes
        # pyg.graphics.draw(4, pyg.gl.GL_LINE_LOOP, ('v2f', [1, 1, 100, 1, 100, 100, 1, 100]))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F1:
            self.game.debug = not self.game.debug
        if symbol == key.F2:
            self.game.show_fps = not self.game.show_fps
        if symbol == key.F3:
            self.game.draw_bounding_boxes = not self.game.draw_bounding_boxes

        if symbol == key.ESCAPE:
            self.game.shutdown()

        if symbol == key.ENTER and self.game.game_state == GameState.MAIN_MENU:
            self.game.start_stage(0)

        if symbol == key.ENTER and self.game.game_state == GameState.GAME_FINISHED:
            self.game.main_menu()

    def on_mouse_motion(x, y, dx, dy):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        self.game.mouse_pos = (x, y)

    def on_close(self):
        self.game.shutdown()
