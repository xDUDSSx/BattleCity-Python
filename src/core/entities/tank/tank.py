from core import constants
from core.entities.movable import Movable
from core.entities.particles.projectile import Projectile
from core.texture_manager import TextureManager


class Tank(Movable):
    """
    A class representing a tank in the game world.
    """

    def __init__(self, **kwargs):
        self.texture1 = TextureManager.tank_player_1  # Movement animation frames
        self.texture2 = TextureManager.tank_player_2
        super().__init__(img=self.texture1, **kwargs)
        self.speed = constants.TANK_SPEED
        self.move_skip = constants.TANK_MOVE_SKIP
        self.scale = constants.TANK_SCALE  # For 16x16 pixel textures
        self.health = constants.TANK_HEALTH
        self.fire_cooldown = 0
        self.last_fired_bullet = None
        self.bullet_spawn_position = {
            (-1, 0): (0, self.rect.height // 2),
            (1, 0): (self.rect.width, self.rect.height // 2),
            (0, 1): (self.rect.width // 2, self.rect.height),
            (0, -1): (self.rect.width // 2, 0)
        }
        self.track_anim = False

    def logic_update(self, game, tick):
        super().logic_update(game, tick)

        # Movement direction rotation
        super().resolve_rotation_4_axis()

        # Fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # Animation
        if self.move_dir[0] != 0 or self.move_dir[1] != 0:
            if tick % constants.TANK_TRACK_ANIM_DURATION == 0:
                self.track_anim = not self.track_anim
                if self.track_anim:
                    self.image = self.texture1
                else:
                    self.image = self.texture2

    def shoot(self, game, player_invoked=False) -> None:
        """
        Makes the tank shoot by creating a projectile entity.
        Each tank can only fire a single projectile at a time and it can't shoot again until
        the projectile it previously fired has been destroyed (by hitting something or its lifetime ending).
        Also there is a short minimum fire cooldown in place.
        """
        if self.can_shoot():
            spawn_position = self.bullet_spawn_position[self.facing_direction]
            new_bullet = Projectile(self, x=self.rect.x + spawn_position[0], y=self.rect.y + spawn_position[1],
                                    batch=game.batch)
            new_bullet.move_dir = self.facing_direction
            new_bullet.player_owned = player_invoked
            game.entity_manager.add_entity(new_bullet)

            self.last_fired_bullet = new_bullet
            self.fire_cooldown = constants.TANK_MIN_FIRE_COOLDOWN

    def can_shoot(self) -> bool:
        """
        Determines whether the tank can currently shoot a new projectile.
        """
        return self.last_fired_bullet is None or self.last_fired_bullet.to_remove and self.fire_cooldown <= 0

    def damage(self, game, other_entity=None) -> bool:
        """
        Applies damage to this tank or destroys it, deleting the entity.
        """
        self.health -= 1
        if self.health <= 0:
            game.entity_manager.remove_entity(self)
        return False
