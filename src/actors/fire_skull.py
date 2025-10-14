

import random
import pygame
from actors.enemy import Enemy
from utils.resource_manager import ResourceManager

FIRE_SKULL_SPEED = 1

FIRE_SKULL_LIFE = 2

FIRE_SKULL_DAMAGE_POWER = 1


class FireSkull(Enemy):
    RENDER_PRIORITY = 1
    DROP_CHANCE = 0.7
    HITBOX_OFFSET = (4, 7)
    HITBOX_SIZE = (12, 12)
    DAMAGE_COOLDOWN = 60

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(random.choice([-1,1]), random.choice([-1,1])).normalize(),
            speed=FIRE_SKULL_SPEED,
            life=FIRE_SKULL_LIFE)

        self.dungeon = dungeon

        self.image = ResourceManager.load_image('fire_skull.png')
        self.animation = ResourceManager.load_animation('fire_skull.json')


    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.animation.get_rect())
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * 16)

    def get_damage_power(self):
        return FIRE_SKULL_DAMAGE_POWER

    def update(self, time):
        super().update(time)
        self.animation.update(time)
        self.move(self.dir * self.speed * time)

    def map_collide(self, map_collisions, time):
        indices = self.rect.collidelistall(map_collisions)
        if indices:
            if len(indices) == 1:
                tile = map_collisions[indices[0]]
                if (abs(tile.centerx - self.rect.centerx) > abs(tile.centery - self.rect.centery)):
                    if ((tile.centerx > self.rect.centerx and self.dir.x > 0)
                    or (tile.centerx < self.rect.centerx and self.dir.x < 0)):
                        self.dir.x = -self.dir.x
                else:
                    if ((tile.centery > self.rect.centery and self.dir.y > 0)
                    or (tile.centery < self.rect.centery and self.dir.y < 0)):
                        self.dir.y = -self.dir.y
            elif len(indices) == 2:
                tile1 = map_collisions[indices[0]]
                tile2 = map_collisions[indices[1]]
                fx = 2 if tile1.centerx != tile2.centerx else 1
                fy = 2 if tile1.centery != tile2.centery else 1
                centerx = (tile1.centerx + tile2.centerx) / 2
                centery = (tile1.centery + tile2.centery) / 2
                if (abs(centerx - self.rect.centerx) / fx > abs(centery - self.rect.centery) / fy):
                    self.dir.x = -self.dir.x
                else:
                    self.dir.y = -self.dir.y
            else:
                self.dir.x = -self.dir.x
                self.dir.y = -self.dir.y

    def player_react(self, player):
        return