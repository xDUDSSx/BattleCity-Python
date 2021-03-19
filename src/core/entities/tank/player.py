import numpy as np
from pyglet.window import key

from core import constants
from core.entities.tank import tank


class Player(tank.Tank):
    """
    A tank taking input from the keyboard and representing a play in-game.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = constants.PLAYER_SPEED
        self.move_skip = constants.PLAYER_MOVE_SKIP
        self.key_handler = key.KeyStateHandler()
        self.raw_movement_direction = np.zeros(2, int)
        self.health = constants.PLAYER_HEALTH
        self.shoot_now = False

    def logic_update(self, game, tick):
        self.handle_movement_controls()
        if self.shoot_now:
            self.shoot(game, player_invoked=True)
            self.shoot_now = False
        super().logic_update(game, tick)

        # Just a quick test for one of the map methods. Perpetually destroys tiles around the player tank.
        # list = game.game_map.get_tiles_around_tile(game.game_map.get_entity_map_position(self), 2)
        # list = list.ravel()
        # for tile in list:
        #     if tile is not None:
        #         if hasattr(tile, "damage"):
        #             tile.damage(game)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.shoot_now = True

    def handle_movement_controls(self):
        """
        Handles movement input from the keyboard. Player Tank's movement is restricted to only 4 axis
        with the last pressed key taking priority over movement direction.
        """
        dx = dy = 0

        if self.key_handler[key.A]:
            dx -= 1
        if self.key_handler[key.D]:
            dx += 1
        if self.key_handler[key.W]:
            dy += 1
        if self.key_handler[key.S]:
            dy -= 1

        change = not np.array_equal(self.raw_movement_direction, np.array([dx, dy]))

        if change:
            if dx != 0 and dy != 0:
                if self.move_dir[0] != 0:
                    self.move_dir[0] = 0
                    self.move_dir[1] = dy
                else:
                    self.move_dir[1] = 0
                    self.move_dir[0] = dx
            else:
                self.move_dir[0] = dx
                self.move_dir[1] = dy

        self.raw_movement_direction[0] = dx
        self.raw_movement_direction[1] = dy
