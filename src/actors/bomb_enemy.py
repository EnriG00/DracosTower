
import pygame
from scene.dungeon.floor.collisions import COL_NONE
from actors.enemy import Enemy
from actors.explosion import Explosion
from utils.resource_manager import ResourceManager
import random

BOMB_ENEMY_WALK_SPEED = .5
BOMB_ENEMY_RUN_SPEED = .9

BOMB_ENEMY_EXPLOSION_OFFSET = (1, 1)

BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MIN = 30
BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MAX = 60

BOMB_ENEMY_LIFE = 2

BOMB_ENEMY_DAMAGE_POWER = 1


class BombEnemy(Enemy):
    RENDER_PRIORITY = 1
    HITBOX_OFFSET = (10, 10)
    HITBOX_SIZE = (12, 12)
    DAMAGE_COOLDOWN = 30

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(random.choice([-1,1]), random.choice([-1,1])).normalize(),
            speed=BOMB_ENEMY_WALK_SPEED,
            life=BOMB_ENEMY_LIFE)

        self.dungeon = dungeon

        self.image = ResourceManager.load_image('bomb_enemy.png')
        self.animation_walk = ResourceManager.load_animation('bomb_enemy_walk.json')
        self.animation_run = ResourceManager.load_animation('bomb_enemy_run.json')
        self.current_animation = self.animation_walk
        self.sprite_direction = 'LEFT'

        self.direction_change_delay = random.randint(BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MIN, BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MAX)
        self.running = False


    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.current_animation.get_rect())
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * 16)

    def explode(self):
        self.kill()
        self.dungeon.add_actor(Explosion(self.dungeon, self.pos + BOMB_ENEMY_EXPLOSION_OFFSET))

    def get_damage_power(self):
        return BOMB_ENEMY_DAMAGE_POWER

    def damage(self, actor):
        if self.running:
            self.explode()
        else:
            super().damage(actor)

    def die(self):
        self.explode()

    def take_damage(self, life_count):
        if self.damage_cooldown == 0:
            self.life -= life_count
            # check death
            if self.life <= 0:
                self.explode()
            # set bomb running
            self.running = True
            self.current_animation = self.animation_run
            self.speed = BOMB_ENEMY_RUN_SPEED
            # activate damage cooldown
            self.damage_cooldown = self.DAMAGE_COOLDOWN
            # play sound
            self.sound_hit.play()


    def reset_direction_change_delay(self):
        self.direction_change_delay = random.randint(BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MIN, BOMB_ENEMY_DIRECTION_CHANGE_DELAY_MAX)

    def update(self, time):
        super().update(time)

        # change movement direction
        if self.direction_change_delay < 0:
            # set random direction change delay
            self.reset_direction_change_delay()
            # set random direction
            self.dir.xy = random.uniform(-1, 1), random.uniform(-1, 1)
            self.dir.normalize_ip()
        else:
            self.direction_change_delay -= time

        # set sprite direction
        self.sprite_direction = 'LEFT' if self.dir.x < 0 else 'RIGHT'

        # update animation
        self.current_animation.update(time)
        self.current_animation.set_alternative(self.sprite_direction)

        # move
        self.move(self.dir * self.speed * time)


    def map_collide(self, map_collisions, time):
        index = self.rect.collidelist(map_collisions)
        if index != -1:
            tile = map_collisions[index]
            if (tile.type != COL_NONE):
                if self.running:
                    self.explode()
                else:
                    # move back and reset direction
                    self.move(-self.dir * self.speed * time)
                    self.dir = -self.dir

    def player_react(self, player):
        return