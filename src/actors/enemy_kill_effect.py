import pygame
from actors.actor import Actor
from utils.resource_manager import ResourceManager


class EnemyKillEffect(Actor):
    RENDER_PRIORITY = 1
    HITBOX_OFFSET = (16,16)
    HITBOX_SIZE = (32,32)

    def __init__(self, pos):
        super().__init__(
            pos,
            dir=pygame.Vector2(0,0),
            speed=0)

        self.image = ResourceManager.load_image('enemy_kill_effect.png')
        self.animation = ResourceManager.load_animation('enemy_kill_effect.json')
        self.sound = ResourceManager.load_sound('enemy_die.wav')

        self.sound.play()


    def update(self, time):
        self.animation.update(time)
        if (self.animation.ended()):
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.pos, self.animation.get_rect())

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return

    def player_collide(self, player):
        return