

from pygame.locals import *
from scene.menu.menu import Menu
from utils.resource_manager import ResourceManager




class DieScreen(Menu):
    TRANSITION_START_DURATION = 150
    TRANSITION_END_DURATION = 80
    CONTINUE_BLINK_DELAY = 40
    CONTINUE_IMAGE_POS = (76,119)

    def __init__(self, director):
        Menu.__init__(self, director)

        self.you_died_image = ResourceManager.load_image('you_died.png')
        self.continue_image = ResourceManager.load_image('you_died_continue.png')


    def draw(self, screen):
        screen.fill((0,0,0))
        screen.blit(self.you_died_image, (63,60))

        super().draw(screen)
