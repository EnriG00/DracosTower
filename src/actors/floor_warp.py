
import pygame
from actors.actor import Actor
from utils.resource_manager import ResourceManager


class FloorWarp(Actor):
    HITBOX_OFFSET = (0, 0)
    HITBOX_SIZE = (16, 16)

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,0),
            speed=0)
            
        self.dungeon = dungeon

        self.sound = ResourceManager.load_sound('stairs_up.wav')

    def update(self, time):
        return

    def player_collide(self, player):
        self.dungeon.change_floor()
        self.sound.play()

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return
