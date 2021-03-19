from pyglet.shapes import Rectangle
from core.entities.entity import Entity
from core.texture_manager import TextureManager


class Collider(Entity):
    def __init__(self, x, y, w, h):
        super().__init__(img=TextureManager.error, x=x, y=y)
        self.rect = Rectangle(x, y, w, h)

    def _create_rect(self):
        pass

    def damage(self, game, other_entity=None):
        return False
