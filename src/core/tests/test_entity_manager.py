import os

from core.entities.entity import Entity
from core.entity_manager import EntityManager
from core.game import Game
from core.texture_manager import TextureManager

working_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + os.pardir
game = Game(working_dir, True)


class ExampleEntity(Entity):
    def __init__(self):
        super().__init__(img=TextureManager.error)
        self.update_count = 0

    def logic_update(self, game, tick: int):
        self.update_count += 1


def test_add_remove_entity():
    game.entity_manager = EntityManager()
    test_entity = ExampleEntity()

    assert len(game.entity_manager.entities) == 0
    game.entity_manager.add_entity(test_entity)
    assert len(game.entity_manager.entities) == 1


def test_entity_updates():
    game.entity_manager = EntityManager()
    test_entity = ExampleEntity()

    assert len(game.entity_manager.entities) == 0
    game.entity_manager.add_entity(test_entity)
    assert len(game.entity_manager.entities) == 1
    assert test_entity.update_count == 0
    game.entity_manager.update_entities(game, 0)
    assert test_entity.update_count == 1


def test_remove_entity():
    game.entity_manager = EntityManager()
    test_entity = ExampleEntity()

    game.entity_manager.add_entity(test_entity)
    game.entity_manager.update_entities(game, 0)
    game.entity_manager.remove_entity(test_entity)
    assert len(game.entity_manager.entities) == 1
    game.entity_manager.update_entities(game, 1)
    assert len(game.entity_manager.entities) == 0


def cumulative_test():
    game.entity_manager = EntityManager()
    test_entity = ExampleEntity()

    assert len(game.entity_manager.entities) == 0
    game.entity_manager.add_entity(test_entity)
    assert len(game.entity_manager.entities) == 1
    assert test_entity.update_count == 0
    game.entity_manager.update_entities(game, 0)
    assert test_entity.update_count == 1
    game.entity_manager.update_entities(game, 1)
    game.entity_manager.update_entities(game, 2)
    game.entity_manager.update_entities(game, 3)
    game.entity_manager.update_entities(game, 4)
    assert test_entity.update_count == 5

    game.entity_manager.remove_entity(test_entity)
    assert len(game.entity_manager.entities) == 1
    game.entity_manager.update_entities(game, 5)
    assert len(game.entity_manager.entities) == 0 and test_entity.update_count == 6
