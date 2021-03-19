from core.entities.particles.particle import Particle
from core.texture_manager import TextureManager
from core import constants


class Explosion(Particle):
    def __init__(self, **kwargs):
        super().__init__(img=TextureManager.exp_anim, **kwargs)
        self.lifespan = constants.EXPLOSION_LIFESPAN
        self.scale = 1
