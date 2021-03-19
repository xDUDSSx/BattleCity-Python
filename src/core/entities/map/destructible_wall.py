from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import Game

from core import constants
from core.entities.map.wall import Wall
from core.texture_manager import TextureManager


class DestructibleWall(Wall):
    """
    A destroyable wall in the environment.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = TextureManager.wall_bl
        self.health = constants.WALL_HEALTH
        self._resolve_texture()

    def _resolve_texture(self, damaged: bool = False) -> None:
        """
        Resolves the wall tile texture based on its position in the game world.
        :param damaged: Optionally can be used to display the damaged texture version.
        """
        h = False
        v = False

        if self.x % 48 == 0:
            h = True
        if self.y % 48 == 0:
            v = True

        if h:
            if v:
                if not damaged:
                    self.image = TextureManager.wall_bl
                else:
                    self.image = TextureManager.wall_bl_damaged
            else:
                if not damaged:
                    self.image = TextureManager.wall_tl
                else:
                    self.image = TextureManager.wall_tl_damaged
        else:
            if v:
                if not damaged:
                    self.image = TextureManager.wall_br
                else:
                    self.image = TextureManager.wall_br_damaged
            else:
                if not damaged:
                    self.image = TextureManager.wall_tr
                else:
                    self.image = TextureManager.wall_tr_damaged

    def damage(self, game: Game, other_entity=None) -> bool:
        """
        Applies damage to this wall or destroying it completely, deleting the entity.
        :returns: True if this entity should be ignored by the other entity
        """
        if self.health == constants.WALL_HEALTH and self.health != 1:
            self._resolve_texture(True)
            x = 1
        self.health -= 1
        if self.health <= 0:
            game.game_map.remove_tile(self)
            self.delete()
        return False

