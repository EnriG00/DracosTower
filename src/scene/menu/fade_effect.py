

from pygame.locals import *

class FadeEffect:

    def __init__(self):
        self.intensity = 0
        self.intensity_dest = 0
        self.step = 1
        self.dir = 0

    def update(self, time):
        self.intensity += min(self.step * time, abs(self.intensity_dest - self.intensity)) * self.dir
        if self.intensity == self.intensity_dest:
            self.enabled = False

    def draw(self, screen):
        screen.fill((self.intensity,self.intensity,self.intensity), special_flags=BLEND_MULT)

    def lighten(self, duration):
        self.intensity = 0
        self.dir = 1
        self.intensity_dest = 255
        self.step = 255 / duration
        self.enabled = True

    def darken(self, duration):
        self.intensity = 255
        self.dir = -1
        self.intensity_dest = 0
        self.step = 255 / duration
        self.enabled = True