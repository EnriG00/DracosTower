
import random
import actors.item
from utils.resource_manager import ResourceManager


class EnemyDropGenerator:
    enemy_item_drops = ResourceManager.load_item_drop_databse()

    @classmethod
    def generate_item(cls, enemy, pos):
        enemy_entry = cls.enemy_item_drops[enemy.__class__.__name__]
        item_name = random.choices(population=enemy_entry[0], weights=enemy_entry[1])[0]
        item_class = getattr(actors.item, item_name)
        return item_class(pos)

