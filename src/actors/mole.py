
import random
import pygame
from actors.enemy import Enemy
from utils.resource_manager import ResourceManager



MOLE_UNDERGROUND_DELAY_MIN = 60
MOLE_UNDERGROUND_DELAY_MAX = 240

MOLE_SPINNING_DELAY = 80

# minimum distance to view player
MOLE_PLAYER_VIEW_DISTANCE = 64

MOLE_LIFE = 2
MOLE_DAMAGE_POWER = 1

# color variants
MOLE_VARIANTS = ['RED','BLUE']



class Mole(Enemy):
    RENDER_PRIORITY = 1
    DROP_CHANCE = 0.7
    HITBOX_OFFSET = (0, 8)
    HITBOX_SIZE = (16, 16)
    DAMAGE_COOLDOWN = 60

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(1,0).rotate(random.randrange(4) * 90),
            speed=0,
            life=MOLE_LIFE)

        self.dungeon = dungeon

        self.image = ResourceManager.load_image('mole.png')
        self.animation_attack = ResourceManager.load_animation('mole_attack.json')
        self.animation_spin = ResourceManager.load_animation('mole_spin.json')
        self.animation_retract = ResourceManager.load_animation('mole_retract.json')

        # set color randomly
        self.variant = random.choice(MOLE_VARIANTS)
        self.animation_attack.set_alternative(self.variant)
        self.animation_spin.set_alternative(self.variant)
        self.animation_retract.set_alternative(self.variant)

        self.animation = self.animation_spin

        self.underground_delay = random.randint(MOLE_UNDERGROUND_DELAY_MIN, MOLE_UNDERGROUND_DELAY_MAX)
        self.spinning_delay = MOLE_SPINNING_DELAY

        # state
        self.attacking = False
        self.spinning = True
        self.retracting = False
        self.underground = False


    def draw(self, screen):
        if not self.hidden and not self.underground:
            screen.blit(self.image, self.pos, self.animation.get_rect())
        # debug
        #pygame.draw.circle(screen, (0,0,255), self.rect.center, MOLE_PLAYER_VIEW_DISTANCE, width=1)
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.rect.center + self.dir * MOLE_PLAYER_VIEW_DISTANCE)

    def enable_animation(self, anim):
        if (self.animation != anim):
            self.animation.reset()
        self.animation = anim

    def get_damage_power(self):
        return MOLE_DAMAGE_POWER

    def take_damage(self, life_count):
        if not self.spinning:
            return
        super().take_damage(life_count)

    # disable collisions
    def disable_rect(self):
        self.rect.size = (0,0)

    # enable collisions
    def enable_rect(self):
        self.rect.size = self.HITBOX_SIZE


    def update(self, time):
        super().update(time)

        if self.underground:
            if self.underground_delay < 0:
                self.underground = False
                self.attacking = True
                self.enable_animation(self.animation_attack)
            else:
                self.underground_delay -= time
            # don't update animation
            return

        elif self.attacking:
            if self.animation.ended():
                self.attacking = False
                self.spinning = True
                self.enable_animation(self.animation_spin)
                self.spinning_delay = MOLE_SPINNING_DELAY
                self.enable_rect()

        elif self.spinning:
            if self.spinning_delay < 0:
                self.spinning = False
                self.retracting = True
                self.enable_animation(self.animation_retract)
            else:
                self.spinning_delay -= time
            
        elif self.retracting:
            if self.animation.ended():
                self.retracting = False
                self.underground = True
                self.disable_rect()
                # set underground delay
                self.underground_delay = random.randint(MOLE_UNDERGROUND_DELAY_MIN, MOLE_UNDERGROUND_DELAY_MAX)

        self.animation.update(time)


    def player_collide(self, player):
        if self.spinning:
            super().player_collide(player)

    def player_react(self, player):
        if self.underground:
            self.set_position(pygame.Vector2(player.rect.topleft))

    def map_collide(self, map_collisions, time):
        return
    
    
