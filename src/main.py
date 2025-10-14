
import pygame
from director import *
from scene.dungeon.dungeon import *
from scene.menu.intro import Intro

if __name__ == '__main__':

    pygame.init()
    
    director = Director()

    scene = Intro(director)
    director.push_scene(scene)
    director.execute()
    
    pygame.quit()
