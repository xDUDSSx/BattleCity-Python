from core.entities import entity
from core.texture_manager import TextureManager


class Bush(entity.Entity):
    """
    A non collidable world tile that covers entities below it.
    """

    def __init__(self, **kwargs):
        super().__init__(img=TextureManager.bush, **kwargs)
        self.collidable = False
