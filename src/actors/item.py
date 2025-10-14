
import pygame
from actors.actor import Actor

from utils.resource_manager import ResourceManager


class PickUpItem(Actor):
    RENDER_PRIORITY = 1
    HITBOX_OFFSET = (0, 0)
    HITBOX_SIZE = (16, 16)

    def __init__(self, pos, dungeon=None):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,0),
            speed=0)

        self.image = None


    def update(self, time):
        return

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return



class BombItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_bomb.png')
        self.sound = ResourceManager.load_sound('item.wav')

    def player_collide(self, player):
        player.add_bomb()
        self.kill()
        self.sound.play()


class ArrowItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_arrow.png')
        self.sound = ResourceManager.load_sound('item.wav')

    def player_collide(self, player):
        player.add_arrow()
        self.kill()
        self.sound.play()


class SwordItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_sword.png')
        self.sound = ResourceManager.load_sound('item.wav')

    def player_collide(self, player):
        player.increment_attack()
        self.kill()
        self.sound.play()


class SpeedItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_speed.png')
        self.sound = ResourceManager.load_sound('item.wav')

    def player_collide(self, player):
        player.increment_speed()
        self.kill()
        self.sound.play()


class HeartItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_heart.png')
        self.sound = ResourceManager.load_sound('heart.wav')

    def player_collide(self, player):
        player.increment_life()
        self.kill()
        self.sound.play()


class KeyItem(PickUpItem):
    def __init__(self, pos, dungeon=None):
        super().__init__(pos)
        self.image = ResourceManager.load_image('item_key.png')
        self.sound = ResourceManager.load_sound('key.wav')

    def player_collide(self, player):
        player.add_key()
        self.kill()
        self.sound.play()