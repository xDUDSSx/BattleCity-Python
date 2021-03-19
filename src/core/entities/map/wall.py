from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import Game

from core.entities import entity
from core.texture_manager import TextureManager


class Wall(entity.Entity):
    """
    A basic indestructible wall. Makes up the map.
    """

    def __init__(self, **kwargs):
        super().__init__(img=TextureManager.inwall, **kwargs)
        self.collidable = True

    def projectile_hit(self, quadrant: int, facing_direction: tuple, game: Game) -> None:
        """
        Resolves a projectile hit given information about where the projectile hit.
        Walls can get damaged in pairs of two depending on the projectile hit position.
        :param quadrant: Quadrant of the projectile hit.
        :param facing_direction: Facing direction of the projectile
        :param game: Game object
        """
        other_tile = None

        if facing_direction[0] == 1:
            if quadrant == 2:
                other_tile = game.game_map.get_tile_next_to_entity(self, (0, 1))
            else:
                other_tile = game.game_map.get_tile_next_to_entity(self, (0, -1))
        elif facing_direction[0] == -1:
            if quadrant == 1:
                other_tile = game.game_map.get_tile_next_to_entity(self, (0, 1))
            else:
                other_tile = game.game_map.get_tile_next_to_entity(self, (0, -1))
        elif facing_direction[1] == 1:
            if quadrant == 3:
                other_tile = game.game_map.get_tile_next_to_entity(self, (-1, 0))
            else:
                other_tile = game.game_map.get_tile_next_to_entity(self, (1, 0))
        elif facing_direction[1] == -1:
            if quadrant == 2:
                other_tile = game.game_map.get_tile_next_to_entity(self, (-1, 0))
            else:
                other_tile = game.game_map.get_tile_next_to_entity(self, (1, 0))

        self.damage(game)
        if other_tile is not None and hasattr(other_tile, "damage"):
            other_tile.damage(game)

    def damage(self, game, other_entity=None) -> bool:
        return False
