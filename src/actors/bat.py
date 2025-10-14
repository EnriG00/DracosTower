
import pygame
from actors.enemy import Enemy
from utils.resource_manager import ResourceManager
import random

from scene.dungeon.floor.collisions import COL_BREAKABLE_WALL, COL_WALL

BAT_SPEED = 0.5

BAT_DIRECTION_CHANGE_DELAY_MIN = 30
BAT_DIRECTION_CHANGE_DELAY_MAX = 60

BAT_LIFE = 2
BAT_DAMAGE_POWER = 1

class Bat(Enemy):
    RENDER_PRIORITY = 2
    DROP_CHANCE = .8
    HITBOX_OFFSET = (4, 0)
    HITBOX_SIZE = (24, 15)
    DAMAGE_COOLDOWN = 60

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(random.choice([-1,1]), random.choice([-1,1])).normalize(),
            speed=BAT_SPEED,
            life=BAT_LIFE)

        self.image = ResourceManager.load_image('bat.png')
        self.animation = ResourceManager.load_animation('bat.json')

        self.dungeon = dungeon

        self.direction_change_delay = random.randint(BAT_DIRECTION_CHANGE_DELAY_MIN, BAT_DIRECTION_CHANGE_DELAY_MAX)


    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.animation.get_rect())
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * 24)

    def update(self, time):
        super().update(time)

        if self.direction_change_delay < 0:
            # set random direction change delay
            self.direction_change_delay = random.randint(BAT_DIRECTION_CHANGE_DELAY_MIN, BAT_DIRECTION_CHANGE_DELAY_MAX)
            # set random direction
            self.dir.xy = random.uniform(-1, 1), random.uniform(-1, 1)
            self.dir.normalize_ip()
            # reset speed
            self.speed = BAT_SPEED
        else:
            self.direction_change_delay -= time

        self.animation.update(time)
        self.move(self.dir * self.speed * time)


    def map_collide(self, map_collisions, time):
        for index in self.rect.collidelistall(map_collisions):
            tile = map_collisions[index]
            if (tile.type == COL_WALL or tile.type == COL_BREAKABLE_WALL):
                # move bat back
                self.move(-self.dir * self.speed * time)
                self.speed = 0
                return


    def get_damage_power(self):
        return BAT_DAMAGE_POWER

    def player_react(self, player):
        return



