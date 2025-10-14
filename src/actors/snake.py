
import random
import pygame
from actors.enemy import Enemy
from scene.dungeon.floor.collisions import COL_NONE
from utils.resource_manager import ResourceManager

SNAKE_SPEED_WALK = .5
SNAKE_SPEED_RUN = .9

SNAKE_DIRECTION_CHANGE_DELAY_MIN = 60
SNAKE_DIRECTION_CHANGE_DELAY_MAX = 90

# minimum distance to view player
SNAKE_PLAYER_VIEW_DISTANCE = 64

SNAKE_LIFE = 2
SNAKE_DAMAGE_POWER = 1


class Snake(Enemy):
    RENDER_PRIORITY = 1
    DROP_CHANCE = 0.7
    HITBOX_OFFSET = (4, 4)
    HITBOX_SIZE = (16, 16)
    DAMAGE_COOLDOWN = 60

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(1,0).rotate(random.randrange(4) * 90),
            speed=SNAKE_SPEED_WALK,
            life=SNAKE_LIFE)

        self.dungeon = dungeon

        self.image = ResourceManager.load_image('snake.png')
        self.animation = ResourceManager.load_animation('snake_walk.json')
        self.sprite_direction = 'DOWN'

        self.direction_change_delay = random.randint(SNAKE_DIRECTION_CHANGE_DELAY_MIN, SNAKE_DIRECTION_CHANGE_DELAY_MAX)

        self.running = False


    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.animation.get_rect())
        # debug
        #pygame.draw.circle(screen, (0,0,255), self.rect.center, SNAKE_PLAYER_VIEW_DISTANCE, width=1)
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * SNAKE_PLAYER_VIEW_DISTANCE)

    def get_damage_power(self):
        return SNAKE_DAMAGE_POWER


    def update(self, time):
        super().update(time)

        if not self.running:
            # change direcion randomly
            if self.direction_change_delay < 0:
                # set random direction change delay
                self.direction_change_delay = random.randint(SNAKE_DIRECTION_CHANGE_DELAY_MIN, SNAKE_DIRECTION_CHANGE_DELAY_MAX)
                # set random direction
                self.dir = pygame.Vector2(1,0).rotate(random.randrange(4) * 90)
                # reset speed
                self.speed = SNAKE_SPEED_WALK
            else:
                self.direction_change_delay -= time

        # set sprite direction from angle
        if (self.dir != (0,0)):
            angle = self.dir.angle_to(pygame.Vector2(1,0))
            if (-135 <= angle < -45):
                self.sprite_direction = 'DOWN'
            elif (-45 <= angle < 45):
                self.sprite_direction = 'RIGHT'
            elif (45 <= angle < 135):
                self.sprite_direction = 'UP'
            else:
                self.sprite_direction = 'LEFT'

        self.animation.set_alternative(self.sprite_direction)
        self.animation.update(time)
        self.move(self.dir * self.speed * time)


    def map_collide(self, map_collisions, time):
        index = self.rect.collidelist(map_collisions)
        if index != -1:
            tile = map_collisions[index]
            if (tile.type != COL_NONE):
                # move back and reset direction
                self.move(-self.dir * self.speed * time)
                self.speed = 0
                self.running = False


    def player_react(self, player):  
        if not self.running:
            # check snake is looking at player using line clipping
            if len(player.rect.clipline(self.rect.center, self.rect.center + self.dir * SNAKE_PLAYER_VIEW_DISTANCE)) > 0:
                self.running = True
                self.speed = SNAKE_SPEED_RUN
        # stop running if player is out of range
        elif pygame.Vector2(self.rect.center).distance_to(player.rect.center) > SNAKE_PLAYER_VIEW_DISTANCE:
            self.running = False
            self.speed = SNAKE_SPEED_WALK
        
