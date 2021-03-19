import time

import pyglet as pyg
from pyglet.gl import *

from core import constants
from core.entities.tank.player import Player
from core.game_director import GameDirector
from core.game_state import GameState
from core.game_window import GameWindow
from core.map import Map
from core.stage import Stage
from core.texture_manager import TextureManager
from core.entity_manager import EntityManager
from core.ui import UI


class Game:
    """
    Main game class. Houses game systems, handles the game window and the game-loop / game-state.
    """

    def __init__(self, working_dir, test_only=False):
        self.debug = False
        self.test_only = test_only
        self.mouse_pos = (0, 0)
        self.tick = 0
        self.timer = -1
        self.running = True
        self._shutdown = False
        self.show_fps = False
        self.draw_bounding_boxes = False

        # Texture loading
        glEnable(GL_TEXTURE_2D)  # just in case
        TextureManager.init(working_dir + "/res")
        TextureManager.load()

        # Game systems init
        self.batch = pyg.graphics.Batch()
        self.background_batch = pyg.graphics.Batch()
        self.foreground_batch = pyg.graphics.Batch()
        self.entity_manager = EntityManager()
        self.game_director = GameDirector(self)
        self.game_map = Map()
        self.ui = UI()

        self.game_state = GameState.MAIN_MENU

        if self.test_only:
            return

        # Game director init
        self.game_director.init(working_dir)

        # Game window
        self.window = GameWindow(self,
                                 self.game_director.stage.map_data["pixel_width"]
                                 + constants.UI_SIDE_PANEL_SIZE,
                                 self.game_director.stage.map_data["pixel_height"])
        self.fps_display = pyg.window.FPSDisplay(self.window)

        # Map load
        # self.game_director.load_stage(1, self)

        # Game start
        pyg.clock.schedule_interval(self.update, 1 / constants.FPS)  # Was creating inconsistent fps

    def main_menu(self):
        self.game_state = GameState.MAIN_MENU
        self.window.main_menu_label = pyglet.text.Label('Press <ENTER> to start',
                                                        font_name='Monospaced',
                                                        font_size=24,
                                                        x=self.window.width // 2, y=self.window.height // 2,
                                                        anchor_x='center', anchor_y='center')

    def start_stage(self, index: int):
        self.game_state = GameState.GAME
        self.entity_manager.reset()
        self.game_director.reset()
        self.game_director.load_stage(index, self)

    def stage_clear(self, stage: Stage):
        self.game_state = GameState.STAGE_CLEAR
        if (stage.index + 1) < len(self.game_director.stages):
            self.start_stage(stage.index + 1)
        else:
            self.game_state = GameState.GAME_FINISHED
            self.window.game_finished_label = pyglet.text.Label(
                'All stages completed! <ENTER>',
                font_name='Monospaced',
                font_size=22,
                x=self.window.width // 2, y=self.window.height // 2,
                anchor_x='center', anchor_y='center')

    def game_over(self, stage: Stage):
        self.game_state = GameState.GAME_OVER
        if self.timer == -1:
            self.timer = constants.GAME_OVER_COOLDOWN
        if self.timer <= 0:
            self.timer = -1
            self.main_menu()
        else:
            self.timer -= 1

    def update(self, dt: float) -> None:
        """
        Game loop update method.
        """
        if self.game_state in [GameState.GAME, GameState.GAME_OVER]:
            if self.game_state == GameState.GAME:
                self.entity_manager.update_entities(self, self.tick)
            self.game_director.update(self)

        self.ui.update(self)
        self.tick += 1

    def register_player(self, player: Player) -> Player:
        """
        Registers players key handler to receive input.
        """
        if not self.test_only:
            self.window.push_handlers(player)
            self.window.push_handlers(player.key_handler)

        return player

    def shutdown(self) -> None:
        """
        Stops the game loop and exits the game.
        """
        self._shutdown = True
        self.running = False
        self.window.close()

    @staticmethod
    def system_millis() -> float:
        return time.time() * 1000

    # Unused, replaced by the default pyglet event loop again
    # def game_loop(self) -> None:
    #     """
    #     Method that contains the game loop.
    #
    #     Some information about the current implementation:
    #     Initially I used the pyglet event loop. But it turns out that its timings are for some reason
    #     horribly inconsistent and lag at random times and during user input. I went through many resources
    #     about this and never found a clear answer/solution in any thread or documentation.
    #
    #     So I decided to use my own game loop. At first I had code in it that would time the execution of a single
    #     update/tick and then call the time.sleep() method to sleep the rest of the time till the next frame to free
    #     up cpu usage. However this for some reason didn't work either and caused odd issues that I still can't quite
    #     explain. In the end I figured that the time.sleep() method itself is rather inconsistent when sleeping for
    #     very small amounts of time.
    #
    #     In the end I decided to use the following "busy" game loop that uses a perpetual while loop looping
    #     at all times and using up an entire cpu core.
    #
    #     Update:
    #     Sometimes this busy loop just inexplicably slows down and starts having lag spikes.
    #     I did some profiling with line_profiler package and I am FAIRLY CERTAIN that there is something wrong
    #     with pyglet itself. The window.dispatch_events() method slows everything down. Even with the rendering
    #     and game logic update methods commented out. And setting the fps a lot higher (500),
    #     it has fluctuations of 100s of fps.
    #
    #     Then after a while it starts working again achieving perfect 60 or 144 fps on my machine without any drops
    #     I don't understand it at all. I don't want to use pyglet again.
    #     Still could be a misconfiguration on my machine but I can't tell.
    #
    #     Update2:
    #     I give up. Returned back to pyglet event loop and instead optimised collision detection.
    #     Seems to work fine although not as well as I'd like.
    #     """
    #
    #     print("Starting gameloop")
    #
    #     frame_end = frame_time = frame_delay = 0
    #     while self.running:
    #         frame_start = Game.system_millis()
    #         if frame_start - frame_end > (frame_delay - frame_time):
    #             t1 = time.time()
    #             frame_delay = 1000. / constants.SLOW_MO_FPS if self.slow_mo else 1000. / constants.FPS
    #
    #             pyglet.clock.tick()
    #
    #             self.window.switch_to()
    #
    #             dispatch_start = time.time()
    #             self.window.dispatch_events()
    #             update_start = time.time()
    #             self.update(0)  # Update call
    #             draw_start = time.time()
    #             self.window.dispatch_event('on_draw')  # Render call
    #             flip_start = time.time()
    #             self.window.flip()
    #
    #             frame_end = Game.system_millis()
    #             frame_time = frame_end - frame_start
    #             end = time.time()
    #             print(f"frame time: {end - t1}\n"
    #                   f"dispatch: {update_start - dispatch_start}\n"
    #                   f"update: {draw_start - update_start}\n"
    #                   f"draw: {flip_start - draw_start}\n"
    #                   f"flip: {end - flip_start}")
    #
    #             # if frame_delay > frame_time:
    #             #     time.sleep(frame_delay - frame_time) / 1000)
    #
    #     if self._shutdown:
    #         self.window.close()
