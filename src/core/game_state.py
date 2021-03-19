from enum import Enum


class GameState(Enum):
    MAIN_MENU = 1
    LEVEL_SELECT = 2
    GAME = 3
    GAME_OVER = 4
    STAGE_CLEAR = 5
    GAME_FINISHED = 6