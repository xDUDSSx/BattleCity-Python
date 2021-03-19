from core.entities.particles.particle import Particle
from core.texture_manager import TextureManager
from core import constants


class Bling(Particle):
    def __init__(self, **kwargs):
        super().__init__(img=TextureManager.bling_seq, **kwargs)
        self.lifespan = constants.BLING_LIFESPAN
        self.scale = 3
