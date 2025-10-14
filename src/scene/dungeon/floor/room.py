
import random
import pygame
import copy
from pygame.locals import *
from scene.dungeon.floor.tileset import *
from utils.actor_loader import ActorLoader
from scene.dungeon.floor.collisions import COL_BREAKABLE_WALL, COL_NONE, TileCollision
from actors.door import Door, FinalDoor
from actors.kill_enemies_observer import KillEnemiesObserver
from utils.room_loader import RoomLoader
from utils.utils import *


ROOM_SIZE = (17, 11)
TILE_SIZE = 16
ROOM_SIZE_SCREEN = (ROOM_SIZE[0] * TILE_SIZE, ROOM_SIZE[1] * TILE_SIZE)

DOOR_POS_UP = (128,16)
DOOR_POS_LEFT = (16,80)
DOOR_POS_RIGHT = (240,80)
DOOR_POS_DOWN = (128,144)

ROOM_DOOR_TILE_LOCATION_UP = (7,0)
ROOM_DOOR_TILE_LOCATION_DOWN = (7,9)
ROOM_DOOR_TILE_LOCATION_LEFT = (0,4)
ROOM_DOOR_TILE_LOCATION_RIGHT = (15,4)


class RoomSpriteContext:

    def __init__(self):
        self.updatable_actors = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()

        # render layers
        self.tile_layer_actors = pygame.sprite.Group()
        self.bottom_layer_actors = pygame.sprite.Group()
        self.top_layer_actors = pygame.sprite.Group()
        self.ui_layer = pygame.sprite.Group()

        self.tile_collision_actors = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_attacks = pygame.sprite.Group()
        


class Room:

    def __init__(self, pos, type='COMMON'):
        self.pos = pos
        self.type = type
        self.up = None
        self.left = None
        self.right = None
        self.down = None
        self.door_layout_code = 0
        self.has_key = False


    # bind specific room from file (tiles, collisions, actors...)
    def bind_data(self, dungeon, tileset):
        # assign tileset
        self.tileset = tileset

        # request room to resource loader
        room_json, room_name = RoomLoader.request_room(self.type, self.door_layout_code)
        self.room_name_src = room_name # used for debugging

        self.global_pos = pygame.Vector2(self.pos).elementwise() * ROOM_SIZE_SCREEN

        # load actors and create sprite groups
        self.sprite_context = RoomSpriteContext()
        for actor in room_json['actors']:
            actor_pos = self.global_pos + pygame.Vector2(actor['position']).elementwise() * TILE_SIZE
            actor = ActorLoader.load_actor(actor['id'], actor_pos, dungeon)
            actor.add_to_groups(self.sprite_context)
        
        # create doors if necessary
        self.doors = []
        if room_json["roomTrigger"] != 'NONE':
            self.create_doors(dungeon)
            for door in self.doors:
                door.add_to_groups(self.sprite_context)
            
            if room_json["roomTrigger"] == 'KILL_ENEMIES':
                # add kill enemies observer to open doors when room is cleared
                kill_enemies_observer = KillEnemiesObserver(dungeon, self.sprite_context.enemies)
                kill_enemies_observer.add_to_groups(self.sprite_context)

        # load tile indices from json
        self.tile_bottom_layer = copy.deepcopy(room_json["tileBottomLayer"])
        self.tile_top_layer = copy.deepcopy(room_json["tileTopLayer"])

        # set door tiles
        if self.type != 'SECRET':
            self.update_door_tiles(self.up, self.update_door_up)
            self.update_door_tiles(self.left, self.update_door_left)
            self.update_door_tiles(self.right, self.update_door_right)
            self.update_door_tiles(self.down, self.update_door_down)

        # create map collision rectangles
        self.collisions = []
        self.breakable_wall_collisions = {}
        for i in range(ROOM_SIZE[0]):
            for j in range(ROOM_SIZE[1]):
                collision_type = self.tileset.collisions[self.tile_bottom_layer[j][i][0]][self.tile_bottom_layer[j][i][1]]
                if collision_type != COL_NONE:
                    collision_tile = TileCollision(self.global_pos + pygame.Vector2(i,j).elementwise() * TILE_SIZE, (TILE_SIZE, TILE_SIZE), collision_type)
                    self.collisions.append(collision_tile)

                    # put breakable walls in dictionary to efficiently remove collisions in secret rooms
                    if collision_type == COL_BREAKABLE_WALL:
                        self.breakable_wall_collisions[collision_tile.topleft] = collision_tile


    def get_key_spawn_position(self):
        # get list of free positions (no collisions)
        free_positions = []
        for i in range(2, ROOM_SIZE[0]-2):
            for j in range(2, ROOM_SIZE[1]-2):
                collision_type = self.tileset.collisions[self.tile_bottom_layer[j][i][0]][self.tile_bottom_layer[j][i][1]]
                if collision_type == COL_NONE:
                    free_positions.append((i,j))
        # choose free position randomly
        pos_local = random.choice(free_positions)
    
        return self.global_pos + pygame.Vector2(pos_local).elementwise() * TILE_SIZE


    def remove_wall(self, wall_position):
        wall_pos_global = (self.global_pos[0] + wall_position[0], self.global_pos[1] + wall_position[1])
        if wall_pos_global in self.breakable_wall_collisions:
            self.collisions.remove(self.breakable_wall_collisions[wall_pos_global])
            
    def create_door(self, neighbour, pos, rotation, dungeon):
        if neighbour is not None:
            if neighbour.type == 'END':
                self.doors.append(FinalDoor(self.global_pos + pos, rotation, dungeon))
            elif neighbour.type != 'SECRET':
                self.doors.append(Door(self.global_pos + pos, rotation, dungeon))

    def create_doors(self, dungeon):
        self.create_door(self.up, DOOR_POS_UP, 0, dungeon)
        self.create_door(self.left, DOOR_POS_LEFT, 90, dungeon)
        self.create_door(self.right, DOOR_POS_RIGHT, -90, dungeon)
        self.create_door(self.down, DOOR_POS_DOWN, 180, dungeon)


    def update_door_tiles(self, neighbour, update_door_function):
        if neighbour is not None:
            if neighbour.type == 'COMMON':
                update_door_function('COMMON')
            elif neighbour.type == 'SECRET':
                update_door_function('NONE')


    def draw_layer(self, floor_surface, tile_indices):
        for i in range(ROOM_SIZE[0]):
            for j in range(ROOM_SIZE[1]):
                x = tile_indices[j][i][1]
                y = tile_indices[j][i][0]
                floor_surface.blit(self.tileset.image, self.global_pos + (i*TILE_SIZE, j*TILE_SIZE),(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_bottom(self, floor_surface):
        self.draw_layer(floor_surface, self.tile_bottom_layer)

    def draw_top(self, floor_surface):
        self.draw_layer(floor_surface, self.tile_top_layer)


    def add_up(self):
        new_room = Room(position_up(self.pos))
        self.up = new_room
        new_room.down = self
        return new_room

    def add_down(self):
        new_room = Room(position_down(self.pos))
        self.down = new_room
        new_room.up = self
        return new_room

    def add_left(self):
        new_room = Room(position_left(self.pos))
        self.left = new_room
        new_room.right = self
        return new_room

    def add_right(self):
        new_room = Room(position_right(self.pos))
        self.right = new_room
        new_room.left = self
        return new_room

    def get_neighbour_count(self):
        count = 0
        if (self.up is not None):
            count += 1
        if (self.left is not None):
            count += 1
        if (self.right is not None):
            count += 1
        if (self.down is not None):
            count += 1
        return count

    def get_free_neighbour_positions(self):
        positions = []
        if (self.up is None):
            positions.append(position_up(self.pos))
        if (self.left is None):
            positions.append(position_left(self.pos))
        if (self.right is None):
            positions.append(position_right(self.pos))
        if (self.down is None):
            positions.append(position_down(self.pos))
        return positions

    def get_neighbours(self):
        neighbours = []
        if (self.up is not None):
            neighbours.append(self.up)
        if (self.left is not None):
            neighbours.append(self.left)
        if (self.right is not None):
            neighbours.append(self.right)
        if (self.down is not None):
            neighbours.append(self.down)
        return neighbours


    # distance to first room
    def get_distance(self):
        return abs(self.pos[0]) + abs(self.pos[1])

    def update_door_layout_code(self):
        self.door_layout_code = 0
        self.door_layout_code |= 0 if (self.up is None) else 1
        self.door_layout_code |= 0 if (self.left is None) else 2
        self.door_layout_code |= 0 if (self.right is None) else 4
        self.door_layout_code |= 0 if (self.down is None) else 8


    # set door tiles given a door type
    def update_door_up(self, door_type):
        map_loc = ROOM_DOOR_TILE_LOCATION_UP
        tile_loc = TILESET_DOOR_LOCATION_UP
        variant_offset = 3 * TILESET_DOOR_TYPE_OFFSET_DICT[door_type]
        # top layer
        self.tile_top_layer[map_loc[1]][map_loc[0]]   = (tile_loc[1], tile_loc[0] + variant_offset)
        self.tile_top_layer[map_loc[1]][map_loc[0]+1] = (tile_loc[1], tile_loc[0] + variant_offset + 1)
        self.tile_top_layer[map_loc[1]][map_loc[0]+2] = (tile_loc[1], tile_loc[0] + variant_offset + 2)
        # bottom layer
        self.tile_bottom_layer[map_loc[1]+1][map_loc[0]]   = (tile_loc[1]+1, tile_loc[0] + variant_offset)
        self.tile_bottom_layer[map_loc[1]+1][map_loc[0]+1] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 1)
        self.tile_bottom_layer[map_loc[1]+1][map_loc[0]+2] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 2)


    def update_door_down(self, door_type):
        map_loc = ROOM_DOOR_TILE_LOCATION_DOWN
        tile_loc = TILESET_DOOR_LOCATION_DOWN
        variant_offset = 3 * TILESET_DOOR_TYPE_OFFSET_DICT[door_type]
        # top layer
        self.tile_top_layer[map_loc[1]+1][map_loc[0]]   = (tile_loc[1]+1, tile_loc[0] + variant_offset)
        self.tile_top_layer[map_loc[1]+1][map_loc[0]+1] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 1)
        self.tile_top_layer[map_loc[1]+1][map_loc[0]+2] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 2)
        # bottom layer
        self.tile_bottom_layer[map_loc[1]][map_loc[0]]     = (tile_loc[1], tile_loc[0] + variant_offset)
        self.tile_bottom_layer[map_loc[1]][map_loc[0] + 1] = (tile_loc[1], tile_loc[0] + variant_offset + 1)
        self.tile_bottom_layer[map_loc[1]][map_loc[0] + 2] = (tile_loc[1], tile_loc[0] + variant_offset + 2)


    def update_door_left(self, door_type):
        map_loc = ROOM_DOOR_TILE_LOCATION_LEFT
        tile_loc = TILESET_DOOR_LOCATION_LEFT
        variant_offset = 2 * TILESET_DOOR_TYPE_OFFSET_DICT[door_type]
        # top layer
        self.tile_top_layer[map_loc[1]][map_loc[0]]   = (tile_loc[1], tile_loc[0] + variant_offset)
        self.tile_top_layer[map_loc[1]+1][map_loc[0]] = (tile_loc[1]+1, tile_loc[0] + variant_offset)
        self.tile_top_layer[map_loc[1]+2][map_loc[0]] = (tile_loc[1]+2, tile_loc[0] + variant_offset)
        # bottom layer
        self.tile_bottom_layer[map_loc[1]][map_loc[0]+1]   = (tile_loc[1], tile_loc[0] + variant_offset + 1)
        self.tile_bottom_layer[map_loc[1]+1][map_loc[0]+1] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 1)
        self.tile_bottom_layer[map_loc[1]+2][map_loc[0]+1] = (tile_loc[1]+2, tile_loc[0] + variant_offset + 1)


    def update_door_right(self, door_type):
        map_loc = ROOM_DOOR_TILE_LOCATION_RIGHT
        tile_loc = TILESET_DOOR_LOCATION_RIGHT
        variant_offset = 2 * TILESET_DOOR_TYPE_OFFSET_DICT[door_type]
        # top layer
        self.tile_top_layer[map_loc[1]][map_loc[0]+1]   = (tile_loc[1], tile_loc[0] + variant_offset + 1)
        self.tile_top_layer[map_loc[1]+1][map_loc[0]+1] = (tile_loc[1]+1, tile_loc[0] + variant_offset + 1)
        self.tile_top_layer[map_loc[1]+2][map_loc[0]+1] = (tile_loc[1]+2, tile_loc[0] + variant_offset + 1)
        # bottom layer
        self.tile_bottom_layer[map_loc[1]][map_loc[0]]   = (tile_loc[1], tile_loc[0] + variant_offset)
        self.tile_bottom_layer[map_loc[1]+1][map_loc[0]] = (tile_loc[1]+1, tile_loc[0] + variant_offset)
        self.tile_bottom_layer[map_loc[1]+2][map_loc[0]] = (tile_loc[1]+2, tile_loc[0] + variant_offset)