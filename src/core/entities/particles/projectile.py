from core import constants
from core import utils
from core import collision
from core.entities import map
from core.entities.particles.explosion import Explosion
from core.entities.particles.particle import Particle
from core.texture_manager import TextureManager


class Projectile(Particle):
    """
    A projectile that damages tanks.
    """

    def __init__(self, owner, **kwargs):
        """
        Creates a projectile.
        :param owner: Owner of the projectile. The projectile does not damage it.
        """
        super().__init__(img=TextureManager.bullet, **kwargs)
        self.speed = constants.BULLET_SPEED
        self.collidable = True
        self.potential_targets = []
        self.ignored_targets = [owner]
        self.owner = owner
        self.player_owned = False
        self.lifespan = constants.BULLET_LIFESPAN

    def logic_update(self, game, tick):
        super().logic_update(game, tick)
        super().resolve_rotation_4_axis()

        collision.check_collision(self, self.rect, self.ignored_targets, self.potential_targets,
                                  game.entity_manager, game.game_map)
        if len(self.potential_targets) > 0:
            destroy_bullet = False
            bullet_hit_point = (self.rect.x + self.rect.width // 2,
                                self.rect.y + self.rect.height)

            no_explosion = False
            for target in self.potential_targets:
                if hasattr(target, "damage"):
                    destroy_bullet = True
                    if isinstance(target, map.wall.Wall):
                        wall_center = utils.get_center_of_rect(target.rect)
                        wall_hit_quadrant = utils.determine_point_quadrant(bullet_hit_point, wall_center)
                        target.projectile_hit(wall_hit_quadrant, self.facing_direction, game)
                    else:
                        if isinstance(target, Projectile):
                            no_explosion = True
                        destroy_bullet = not target.damage(game, other_entity=self)
                    break

            if destroy_bullet:
                if not no_explosion:
                    exp = Explosion(x=bullet_hit_point[0] - constants.EXPLOSION_SIZE // 2,
                                    y=bullet_hit_point[1] - constants.EXPLOSION_SIZE // 2,
                                    batch=game.foreground_batch)
                    game.entity_manager.add_entity(exp)
                game.entity_manager.remove_entity(self)

    def damage(self, game, other_entity=None) -> bool:
        if other_entity.player_owned or self.player_owned:
            return False
            game.entity_manager.remove_entity(self)
        return True
