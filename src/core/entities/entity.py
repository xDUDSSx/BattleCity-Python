import pyglet as pyg

from core import utils


class Entity(pyg.sprite.Sprite):
    """
    Entity resembles an object in the game world.
    """

    def __init__(self, *args, **kwargs):
        self.rect = None  # Position and dimension information that should be used by all game systems.
        super().__init__(*args, **kwargs)

        self.collidable = True  # Whether other entities can collide with this one
        self.facing_direction = (0, 1)
        self.to_remove = False
        self._create_rect()

    def logic_update(self, game, tick: int):
        """
        Calls an update on the entity. The entity can do game logic here.
        :param tick:
        :param game: Game object used to access information about the game world.
        :return:
        """
        pass

    def move(self, x: int, y: int):
        """
        Moves the entity by a vector.
        """
        self._x += x
        self._y += y
        self._update_position()

    def _update_position(self):
        super()._update_position()
        self._create_rect()

    def _create_rect(self):
        """
        Creates a rectangle representing the entities bounding box corrected for anchor point.

        When setting an image texture anchor point in pyglet (to set rotation origin). The pyglet sprite coordinates
        will represent the position of the new anchor. This means that depending on the anchor point. The sprites
        bounding box will move. Accounting for this in all algorithms working with entity bounding boxes is potentially
        problematic so each entity keeps an instance of a rectangle that has corrected coordinates depending on the
        anchor point. This rectangle is recalculated everytime the entities position changes.
        """
        if self.rect is None:
            self.rect = pyg.shapes.Rectangle(self.x, self.y, self.width, self.height)
        else:
            utils.set_rect(self.rect, self.x, self.y, self.width, self.height)

        if self.image is not None and hasattr(self.image, "anchor_x"):
            if self.image.anchor_x != 0 or self.image.anchor_y != 0:
                self.rect.x -= self.rect.width // (self.image.width // self.image.anchor_x)
                self.rect.y -= self.rect.height // (self.image.height // self.image.anchor_y)

    def face(self, direction: str):
        """
        Sets the entities facing direction and rotates/flips it's sprite appropriately.
        :param direction: String parameter, can be "L", "R", "U", "D" for each of the 4 directions.
        """

        if direction == "L" and self.facing_direction != (-1, 0):
            self.rotation = 90
            self.scale_x = 1
            self.scale_y = -1
            self.facing_direction = (-1, 0)
        elif direction == "R" and self.facing_direction != (1, 0):
            self.rotation = 90
            self.scale_x = 1
            self.scale_y = 1
            self.facing_direction = (1, 0)
        elif direction == "U" and self.facing_direction != (0, 1):
            self.rotation = 0
            self.scale_x = 1
            self.scale_y = 1
            self.facing_direction = (0, 1)
        elif direction == "D" and self.facing_direction != (0, -1):
            self.rotation = 180
            self.scale_x = -1
            self.scale_y = 1
            self.facing_direction = (0, -1)
        else:
            return

    def center_x(self) -> int:
        return self.rect.x + self.rect.width // 2

    def center_y(self) -> int:
        return self.rect.y + self.rect.height // 2
