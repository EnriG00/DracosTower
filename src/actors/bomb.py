

import pygame
from actors.actor import Actor
from actors.explosion import Explosion
from utils.resource_manager import ResourceManager

BOMB_EXPLOSION_OFFSET = (-8,-8)

class Bomb(Actor):
    RENDER_PRIORITY = 1

    def __init__(self, dungeon, pos):
        Actor.__init__(self)
        self.image = ResourceManager.load_image('bomb.png')
        self.animation = ResourceManager.load_animation('bomb.json')
        self.sound = ResourceManager.load_sound('put_bomb.wav')
        self.sound.play()

        self.dungeon = dungeon

        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(pos, (16,16))


    def draw(self, screen):
        screen.blit(self.image, self.pos, self.animation.get_rect())

    def update(self, time):
        self.animation.update(time)
        if (self.animation.ended()):
            self.dungeon.add_actor(Explosion(self.dungeon, self.pos + BOMB_EXPLOSION_OFFSET))
            self.kill()

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return

    def player_collide(self, player):
        return