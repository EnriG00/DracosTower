
from utils.resource_manager import ResourceManager

class ActorLoader:
    actor_db = ResourceManager.load_actor_database()
    loaded_actors = {}

    @classmethod
    def load_actor(cls, id, pos, dungeon):
        if id in cls.loaded_actors:
            actor_class = cls.loaded_actors[id]
        else:
            actor_module_name, actor_class_name = cls.actor_db[str(id)]
            actor_module = __import__('actors.' + actor_module_name)
            actor_class = getattr(getattr(actor_module, actor_module_name), actor_class_name)
            cls.loaded_actors[id] = actor_class
            
        return actor_class(pos, dungeon)