from core import constants
from core.entities.movable import Movable


class Particle(Movable):
    """
    A game object representing some sort of a particle like visual effects or objects that have ties to other objects.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lifespan = constants.PARTICLE_LIFESPAN
        self.collidable = False
        self.collision = False
        self.dead = False

    def logic_update(self, game, tick):
        super().logic_update(game, tick)

        if self.lifespan <= 0:
            game.entity_manager.remove_entity(self)
            self.dead = True
            return

        self.lifespan -= 1
