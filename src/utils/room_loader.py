
import random
from utils.resource_manager import ResourceManager

class RoomLoader:
    room_db = ResourceManager.load_room_database()

    @classmethod
    def request_room(cls, room_type, door_layout):
        # select room randomly
        if room_type == 'COMMON':
            room_id = random.choice(cls.room_db[room_type][str(door_layout)])
            room_name = str(room_id).zfill(4) + '_' + room_type + '_' + str(door_layout) + '.json'
        else:
            room_id = random.choice(cls.room_db[room_type])
            room_name = str(room_id).zfill(4) + '_' + room_type + '.json'

        return ResourceManager.load_room(room_name), room_name