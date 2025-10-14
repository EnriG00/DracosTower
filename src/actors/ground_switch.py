import pygame
from actors.actor import Actor
from utils.resource_manager import ResourceManager

class GroundSwitch(Actor):
    RENDER_PRIORITY = 0
    HITBOX_OFFSET = (0, 0)
    HITBOX_SIZE = (16, 16)

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,0),
            speed=0)

        self.dungeon = dungeon

        self.image_default = ResourceManager.load_image('ground_switch_default.png')
        self.image_pressed = ResourceManager.load_image('ground_switch_pressed.png')
        self.image = self.image_default
        self.sound = ResourceManager.load_sound('button.wav')

        self.pressed = False


    def update(self, time):
        return

    def draw(self, screen):
        screen.blit(self.image, self.pos)
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)

    def player_collide(self, player):
        if not self.pressed:
            self.pressed = True
            self.image = self.image_pressed
            self.sound.play()
            self.dungeon.complete_room()

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return