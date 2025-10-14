

import pygame
from actors.actor import DamageActor, LifeActor
from actors.arrow import Arrow
from actors.bomb import Bomb
from utils.controls import *
from utils.resource_manager import ResourceManager

from scene.dungeon.floor.collisions import COL_DOOR, COL_NONE


PLAYER_WALK_SPEED = 1

PLAYER_BOW_WALK_SPEED = 0.5
PLAYER_BOW_CHARGE_MIN = 60

PLAYER_ATTACK_COOLDOWN = 20
PLAYER_BOMB_COOLDOWN = 60

PLAYER_DAMAGE_COOLDOWN = 120

# arrow sprite offset
PLAYER_ARROW_OFFSET_UP = (27, 2)
PLAYER_ARROW_OFFSET_LEFT = (6, 20)
PLAYER_ARROW_OFFSET_RIGHT = (29, 20)
PLAYER_ARROW_OFFSET_DOWN = (21, 23)

# default player stats
PLAYER_LIFE = 3
PLAYER_LIFE_MAX = 6
PLAYER_BOMB_COUNT = 3
PLAYER_ARROW_COUNT = 5
PLAYER_ATTACK_POWER = 1
PLAYER_MAX_SPEED_IMPROVEMENT = 0.5


SWORD_RECT_UP = pygame.Rect((25,1),(7,16))
SWORD_RECT_LEFT = pygame.Rect((3,23),(16,7))
SWORD_RECT_RIGHT = pygame.Rect((31,23),(16,7))
SWORD_RECT_DOWN = pygame.Rect((21,32),(7,16))


class SwordAttack(DamageActor):

    def __init__(self, sprite_direction, attack_power):
        pygame.sprite.Sprite.__init__(self)

        self.update_data(sprite_direction, (0,0), attack_power)
        self.attack_power = attack_power

    def update_data(self, sprite_direction, pos, attack_power):
        if sprite_direction == 'UP':
            self.rect_offset = SWORD_RECT_UP
        elif sprite_direction == 'LEFT':
            self.rect_offset = SWORD_RECT_LEFT
        elif sprite_direction == 'RIGHT':
            self.rect_offset = SWORD_RECT_RIGHT
        elif sprite_direction == 'DOWN':
            self.rect_offset = SWORD_RECT_DOWN
        self.rect = self.rect_offset.move(pos)
        self.attack_power = attack_power

    def update(self, time):
        return

    def get_damage_power(self):
        return self.attack_power

    def add_to_groups(self, room_context):
        room_context.player_attacks.add(self)



class Player(LifeActor):
    RENDER_PRIORITY = 1
    HITBOX_SIZE = (16,16)
    HITBOX_OFFSET = (18,18)

    DAMAGE_COOLDOWN = PLAYER_DAMAGE_COOLDOWN

    def __init__(self, pos, dungeon):
        super().__init__(pygame.Vector2(pos), pygame.Vector2(0,1), PLAYER_WALK_SPEED, PLAYER_LIFE)

        self.dungeon = dungeon

        self.image = ResourceManager.load_image('player.png')
        self.wait_animation = ResourceManager.load_animation('player_wait.json')
        self.walk_animation = ResourceManager.load_animation('player_walk.json')
        self.attack_animation = ResourceManager.load_animation('player_attack.json')
        self.bow_aim_animation = ResourceManager.load_animation('player_bow_aim.json')
        self.bow_walk_animation = ResourceManager.load_animation('player_bow_walk.json')
        self.bow_shoot_animation = ResourceManager.load_animation('player_bow_shoot.json')
        self.die_animation = ResourceManager.load_animation('player_die.json')

        self.sound_hit = ResourceManager.load_sound('player_hit.wav')
        self.sound_die = ResourceManager.load_sound('player_die.wav')
        self.sound_attack = ResourceManager.load_sound('sword_attack.wav')

        self.current_pose = self.wait_animation
        self.sprite_direction = 'DOWN'

        # stats/inventory
        self.life = PLAYER_LIFE
        self.bomb_count = PLAYER_BOMB_COUNT
        self.arrow_count = PLAYER_ARROW_COUNT
        self.attack_power = PLAYER_ATTACK_POWER
        self.has_key = False
        self.speed_improvement = 0

        self.sword = SwordAttack(self.sprite_direction, self.attack_power)

        # state
        self.attacking = False
        self.attack_cooldown = 0

        self.aiming = False
        self.bow_charge = 0

        self.shooting = False

        self.bomb_cooldown = 0

        # observers
        self.observers = []


    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.current_pose.get_rect())
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * 24)

    def enable_animation(self, anim):
        if (self.current_pose != anim):
            self.current_pose.reset()
        self.current_pose = anim


    def process_input(self, pressed_keys):

        if (self.attacking or self.shooting):
            self.speed = 0
            # ignore inputs
            return

        # attack
        if pressed_keys[KEY_ATTACK] and self.attack_cooldown == 0 and not self.aiming:
            self.attacking = True
            self.speed = 0
            # enable animation
            self.enable_animation(self.attack_animation)
            # cooldown counter initialization
            self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
            # enable sword attack rect
            self.sword.update_data(self.sprite_direction, self.pos, self.attack_power)
            self.dungeon.add_actor(self.sword)
            # play sound
            self.sound_attack.play()
            # ignore movement
            return

        # put bomb
        if pressed_keys[KEY_BOMB] and self.bomb_cooldown == 0 and self.bomb_count > 0:
            self.bomb_count -= 1
            # add bomb to scene
            self.dungeon.add_actor(Bomb(self.dungeon, self.rect.topleft))
            self.bomb_cooldown = PLAYER_BOMB_COOLDOWN

        # bow aimimg
        if pressed_keys[KEY_BOW] and self.arrow_count > 0:
            self.aiming = True
            # increment bow charge
            self.bow_charge += 1
        else:
            # shoot arrow
            if self.bow_charge > PLAYER_BOW_CHARGE_MIN:
                # enable shooting if bow is charged
                self.shooting = True
                # reset bow charge counter
                self.bow_charge = 0
                # enable shooting animation
                self.enable_animation(self.bow_shoot_animation)

                # decrement arrow count
                self.arrow_count -= 1

                # create arrow
                if self.sprite_direction == 'UP':
                    self.dungeon.add_actor(Arrow(self.pos + PLAYER_ARROW_OFFSET_UP, 180))
                elif self.sprite_direction == 'LEFT':
                    self.dungeon.add_actor(Arrow(self.pos + PLAYER_ARROW_OFFSET_LEFT, 90))
                elif self.sprite_direction == 'RIGHT':
                    self.dungeon.add_actor(Arrow(self.pos + PLAYER_ARROW_OFFSET_RIGHT, -90))
                else:
                    self.dungeon.add_actor(Arrow(self.pos + PLAYER_ARROW_OFFSET_DOWN, 0))

                # ignore movement
                return
            else:
                # stop aiming
                self.aiming = False
                # reset bow charge
                self.bow_charge = 0

        # movement direction
        dir_x = 0
        dir_y = 0
        if pressed_keys[KEY_LEFT]:
            dir_x -= 1
        if pressed_keys[KEY_RIGHT]:
            dir_x += 1
        if pressed_keys[KEY_UP]:
            dir_y -= 1
        if pressed_keys[KEY_DOWN]:
            dir_y += 1

        # movement speed
        if (dir_x == 0 and dir_y == 0):
            self.speed = 0

            # enable animation
            if (self.aiming):
                self.enable_animation(self.bow_aim_animation)
            else:
                self.enable_animation(self.wait_animation)

        else:
            # normalize direction
            self.dir.xy = dir_x, dir_y
            self.dir.normalize_ip()

            # enable animation
            if (self.aiming):
                self.speed = PLAYER_BOW_WALK_SPEED
                self.enable_animation(self.bow_walk_animation)
            else:
                self.speed = PLAYER_WALK_SPEED
                self.enable_animation(self.walk_animation)


    def update(self, time):
        super().update(time)

        # decrement attack cooldown counter
        if (self.attack_cooldown > 0):
            self.attack_cooldown = max(self.attack_cooldown - time, 0)

        # decrement bomb cooldown counter
        if (self.bomb_cooldown > 0):
            self.bomb_cooldown = max(self.bomb_cooldown - time, 0)

        # update position
        self.move(self.dir * time * self.speed * (1 + self.speed_improvement))

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

        # update animation
        self.current_pose.set_alternative(self.sprite_direction)
        self.current_pose.update(time)

        # check animation end
        if (self.attacking or self.shooting):
            if (self.current_pose.ended()):
                self.attacking = False
                self.shooting = False
                self.enable_animation(self.wait_animation)
                self.current_pose.set_alternative(self.sprite_direction)

                self.sword.kill()

        self.notify_observers()


    def add_key(self):
        self.has_key = True
        self.notify_observers()
        
    def use_key(self):
        self.has_key = False
        self.notify_observers()

    def add_bomb(self):
        self.bomb_count += 1
        self.notify_observers()

    def add_arrow(self):
        self.arrow_count += 1
        self.notify_observers()

    def increment_attack(self):
        self.attack_power += .5
        self.notify_observers()

    def increment_speed(self):
        self.speed_improvement = min(self.speed_improvement + .125, PLAYER_MAX_SPEED_IMPROVEMENT)
        self.notify_observers()

    def increment_life(self):
        self.life = min(self.life + 1, PLAYER_LIFE_MAX)
        self.notify_observers()

    def notify_observers(self):
        for observer in self.observers:
            observer.notify(self)

    def add_observer(self, observer):
        self.observers.append(observer)

    def die(self):
        self.enable_animation(self.die_animation)
        self.sound_die.play()
        self.dungeon.exit()

    def take_damage(self, life_count):
        if self.damage_cooldown == 0:
            self.life -= life_count
            self.notify_observers()
            if self.life <= 0:
                self.die()
            self.damage_cooldown = self.DAMAGE_COOLDOWN
            self.sound_hit.play()


    def map_collide(self, map_collisions, time):
        if (self.speed == 0):
            return

        for index in self.rect.collidelistall(map_collisions):
            tile = map_collisions[index]
            if (tile.type != COL_NONE and tile.type != COL_DOOR):
                # check collision side and move player back
                if (abs(tile.centerx - self.rect.centerx) > abs(tile.centery - self.rect.centery)):
                    if (tile.centerx < self.rect.centerx):
                        self.move((tile.right - self.rect.left, 0))
                    else:
                        self.move((tile.left - self.rect.right, 0))
                else:
                    if (tile.centery < self.rect.centery):
                        self.move((0, tile.bottom - self.rect.top))
                    else:
                        self.move((0, tile.top - self.rect.bottom))


    def player_react(self, player):
        return

    def player_collide(self, player):
        return