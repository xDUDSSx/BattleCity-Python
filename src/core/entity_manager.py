import pyglet as pyg

from core import constants
from core.entities.entity import Entity


class EntityManager():
    """
    Manages logic updates of game entities.
    """

    def __init__(self):
        self.entities = []
        self.last_debug_tick = 0

    def update_entities(self, game, tick) -> None:
        """
        Iterates over all active entities and calls their update method.
        :param game: The game object
        :param tick: Game tick
        """
        count = len(self.entities)
        for i in range(count):
            self.entities[i].logic_update(game, tick)

        for entity_to_remove in [ent for ent in self.entities if ent.to_remove]:
            self.entities.remove(entity_to_remove)
            entity_to_remove.delete()

        if game.debug:
            self.last_debug_tick -= 1
            if self.last_debug_tick <= 0:
                self.last_debug_tick = constants.DEBUG_INFO_INTERVAL

                entity_manager_entities = len(self.entities)
                map_entities = 0
                view = game.game_map.map.ravel()
                for t in view:
                    if t is not None:
                        map_entities += 1

                print("-----\n" + "Number of entities:".ljust(25) + str(entity_manager_entities + map_entities))
                print("Entity manager:".ljust(25) + str(entity_manager_entities))
                print("Map:".ljust(25) + str(map_entities) + f" ({game.game_map.map.size})")

    def render_entity_debug_boxes(self):
        count = len(self.entities)
        for i in range(count):
            x = self.entities[i].rect.x
            y = self.entities[i].rect.y
            w = self.entities[i].rect.width
            h = self.entities[i].rect.height

            pyg.gl.glColor3f(1.0, 1.0, 0.0)
            pyg.graphics.draw(4, pyg.gl.GL_LINE_LOOP, ('v2f',
                                                       [x, y,
                                                        x + w, y,
                                                        x + w, y + h,
                                                        x, y + h]))

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        entity.to_remove = True

    def reset(self) -> None:
        """
        Disposes of all entities in the entity manager.
        """
        for ent in self.entities:
            ent.delete()

        self.entities.clear()