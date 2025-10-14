
from pygame.locals import *
from scene.dungeon.dungeon import Dungeon
from utils.resource_manager import ResourceManager
from scene.menu.menu import Menu


class Intro(Menu):
    TRANSITION_START_DURATION = 130
    TRANSITION_END_DURATION = 80
    CONTINUE_BLINK_DELAY = 40
    CONTINUE_IMAGE_POS = (93, 166)


    def __init__(self, director):
        Menu.__init__(self, director)

        self.background_image = ResourceManager.load_image('intro_background.png')
        self.title_image = ResourceManager.load_image('intro_title.png')
        self.continue_image = ResourceManager.load_image('intro_press.png')


    def reset_intro(self):
        self.fade_effect.lighten(self.TRANSITION_START_DURATION)
        self.transition_enabled = True

        self.blink_delay = 0
        self.hide_press = False

        self.exit = False
        self.exit_delay = 0


    def exit_menu(self):
        self.reset_intro()
        self.director.push_scene(Dungeon(self.director))

    def draw(self, screen):
        screen.blit(self.background_image, (0,0))
        screen.blit(self.title_image, (79, 28))
        super().draw(screen)

