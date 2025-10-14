
from scene.dungeon.floor.floor_generator import FloorGenerator
from utils.resource_manager import ResourceManager
import pygame
from scene.dungeon.floor.room import ROOM_SIZE_SCREEN
from pygame.locals import *

class Floor:

    def __init__(self, dungeon, tileset_name, room_count, floor_index):

        self.index = floor_index
        
        # load tileset
        self.tileset = ResourceManager.load_tileset(tileset_name)
        # generate floor
        room_list, root_room, floor_size = FloorGenerator.generate_floor(room_count)
        self.rooms = room_list
        self.root_room = root_room
        self.size = pygame.Vector2(floor_size)

        # bind specific rooms
        for room in room_list:
            room.bind_data(dungeon, self.tileset)

        # create draw layers
        self.surface_bottom = pygame.Surface(self.size.elementwise() * ROOM_SIZE_SCREEN)
        self.surface_top = pygame.Surface(self.size.elementwise() * ROOM_SIZE_SCREEN, flags=SRCALPHA)

        # draw rooms in global floor surface
        for room in room_list:
            self.update_room_surface(room)

        # activate root room
        self.visited_rooms = []
        self.visible_rooms = []
        self.explore_room(self.root_room)


    def explore_room(self, room):
        self.visited_rooms.append(room)
        if room.type != 'SECRET':
            for neighbour in room.get_neighbours():
                if neighbour.type != 'SECRET':
                    self.visible_rooms.append(neighbour)

    def update_room_surface(self, room):
        room.draw_bottom(self.surface_bottom)
        room.draw_top(self.surface_top)

    def draw_bottom(self, screen):
        screen.blit(self.surface_bottom, (0,0))

    def draw_top(self, screen):
        screen.blit(self.surface_top, (0,0))
