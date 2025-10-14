
import pygame
from pygame.locals import *

UI_HEIGHT = 32
SCREEN_WIDTH = 272
SCREEN_HEIGHT = 176 + UI_HEIGHT
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

FRAME_RATE = 60
FRAME_TIME_DEFAULT = 1/60 * 1000 # milliseconds of each frame


class Director():

    def __init__(self):
        # init screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE, flags=RESIZABLE|SCALED)
        pygame.display.set_caption("DRACO'S TOWER - FIC GAMES")
        pygame.mixer.init()

        self.stack = []
        self.quit = False
        self.clock = pygame.time.Clock()

    def loop(self, scene):

        self.exit_scene = False

        # clear events before loop
        pygame.event.clear()

        while not self.exit_scene:
            # frame rate fps sync
            time = self.clock.tick(FRAME_RATE) / FRAME_TIME_DEFAULT

            scene.events(pygame.event.get())
            scene.update(time)
            scene.draw(self.screen)
            pygame.display.flip()

    def execute(self):
        while (len(self.stack) > 0):
            scene = self.stack[len(self.stack)-1]
            self.loop(scene)

    def exit_current_scene(self):
        self.exit_scene = True
        if (len(self.stack) > 0):
            self.stack.pop()

    def exit_program(self):
        # empty stack
        self.stack = []
        self.exit_scene = True

    def switch_scene(self, scene):
        self.exit_current_scene()
        self.stack.append(scene)

    def push_scene(self, scene):
        self.exit_scene = True
        self.stack.append(scene)
