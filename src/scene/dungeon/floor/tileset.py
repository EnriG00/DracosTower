
TILESET_DOOR_TYPE_OFFSET_DICT = {
    'NONE' : 0,
    'COMMON' : 1,
    'SECRET' : 2,
}

# door positions in tileset grid
TILESET_DOOR_LOCATION_UP    = (0, 9)
TILESET_DOOR_LOCATION_DOWN  = (0, 11)
TILESET_DOOR_LOCATION_LEFT  = (0, 13)
TILESET_DOOR_LOCATION_RIGHT = (6, 13)


class Tileset:

    def __init__(self, image, collisions, size):
        self.image = image
        self.collisions = collisions
        self.size = size
