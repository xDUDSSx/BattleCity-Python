import os
import pyglet as pyg
from core.game import Game

# Application entry point

working_dir = os.path.dirname(os.path.realpath(__file__))
game = Game(working_dir)
pyg.app.run()
