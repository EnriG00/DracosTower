

import sys
import pygame
from pygame.locals import *
from utils.controls import KEY_MENU
from scene.menu.fade_effect import FadeEffect
from scene.scene import Scene
from utils.resource_manager import ResourceManager


class Menu(Scene):

    def __init__(self, director):
        Scene.__init__(self, director)

        self.sound = ResourceManager.load_sound('menu_continue.wav')

        self.fade_effect = FadeEffect()
        self.fade_effect.lighten(self.TRANSITION_START_DURATION)

        self.exit = False
        self.exit_delay = 0

        self.blink_delay = 0
        self.hide_continue = False

    def exit_menu(self):
        self.director.exit_current_scene()

    def update(self, time):
        if self.fade_effect.enabled:
            self.fade_effect.update(time)
        elif self.exit:
            self.exit_menu()
            return

        self.hide_continue = (self.blink_delay % (self.CONTINUE_BLINK_DELAY * 2)) > self.CONTINUE_BLINK_DELAY
        self.blink_delay += time


    def draw(self, screen):
        if self.fade_effect.enabled or self.exit:
            self.fade_effect.draw(screen)
        elif not self.hide_continue:
            screen.blit(self.continue_image, self.CONTINUE_IMAGE_POS)


    def events(self, event_list):
        for event in event_list:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if pressed_keys[KEY_MENU] and not self.fade_effect.enabled:
            self.exit = True
            self.fade_effect.darken(self.TRANSITION_END_DURATION)
            self.sound.play()