
import pygame
from pygame.locals import *
from scene.menu.menu import Menu
from utils.resource_manager import ResourceManager


TROPHY_POS = (120,116)

class Trophy(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = ResourceManager.load_image('win_trophy.png')
        self.animation = ResourceManager.load_animation('win_trophy.json')

        self.pos = pygame.Vector2(pos)

    def update(self, time):
        self.animation.update(time)

    def draw(self, screen):
        screen.blit(self.image, self.pos, self.animation.get_rect())


class WinScreen(Menu):
    TRANSITION_START_DURATION = 150
    TRANSITION_END_DURATION = 80
    CONTINUE_BLINK_DELAY = 40
    CONTINUE_IMAGE_POS = (76,160)

    def __init__(self, director):
        Menu.__init__(self, director)

        self.you_win_image = ResourceManager.load_image('you_win.png')
        self.continue_image = ResourceManager.load_image('you_died_continue.png')

        self.trophy = Trophy(TROPHY_POS)

        pygame.mixer.music.stop()

    def update(self, time):
        self.trophy.update(time)
        super().update(time)

    def draw(self, screen):
        screen.fill((0,0,0))
        screen.blit(self.you_win_image, (73,60))
        self.trophy.draw(screen)

        super().draw(screen)
