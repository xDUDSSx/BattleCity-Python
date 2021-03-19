from core.entities.entity import Entity
from core.texture_manager import TextureManager


class Flag(Entity):
    """
    The players "home base". The players goal is to protect this object and prevent it from getting destroyed.
    """

    def __init__(self, **kwargs):
        self.destroyed = False
        super().__init__(img=TextureManager.flag, **kwargs)
        self.scale = 3

    def damage(self, game, other_entity=None) -> bool:
        self.image = TextureManager.flag_damaged
        self.destroyed = True
        return False
