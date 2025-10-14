


import sys
import pygame
from scene.scene import Scene
from utils.controls import KEY_PAUSE
from utils.resource_manager import ResourceManager
from pygame.locals import *


PAUSE_IMAGE_POS = (93,105)

class Pause(Scene):

    def __init__(self, director):
        Scene.__init__(self, director)

        self.pause_image = ResourceManager.load_image('pause.png')
        self.drawn = False
        pygame.mixer.music.set_volume(0.5)


    def update(self, time):
        return


    def draw(self, screen):
        if not self.drawn:
            screen.blit(self.pause_image, PAUSE_IMAGE_POS)
            self.drawn = True


    def events(self, event_list):
        for event in event_list:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == KEY_PAUSE:
                pygame.mixer.music.set_volume(1)
                self.director.exit_current_scene()

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()
