

import pygame
from actors.actor import DamageActor
from scene.dungeon.floor.collisions import COL_NONE
from utils.resource_manager import ResourceManager

ARROW_SPEED = 3
ARROW_DAMAGE_POWER = 1.5

class Arrow(DamageActor):
    RENDER_PRIORITY = 1

    HITBOX_OFFSET = (0,0)
    HITBOX_SIZE = (16,16)

    def __init__(self, pos, rotation, dungeon=None):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,1).rotate(rotation),
            speed=ARROW_SPEED)

        self.image = ResourceManager.load_image('arrow.png')
        self.image = pygame.transform.rotate(self.image, -rotation)
        self.sound_shoot = ResourceManager.load_sound('arrow_shoot.wav')
        self.sound_wall = ResourceManager.load_sound('arrow_hit.wav')

        self.sound_shoot.play()
        
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos)

        

    def draw(self, screen):
        screen.blit(self.image, self.pos)
        # debug
        #pygame.draw.rect(screen, (0,0,255), self.rect, width=1)


    def add_to_groups(self, room_context):
        super().add_to_groups(room_context)
        room_context.player_attacks.add(self)


    def update(self, time):
        self.move(self.dir * time * self.speed)

    def map_collide(self, map_collisions, time):
        index = self.rect.collidelist(map_collisions)

        if index != -1:
            tile = map_collisions[index]
            if tile.type != COL_NONE:
                self.kill()
                self.sound_wall.play()

    def get_damage_power(self):
        return ARROW_DAMAGE_POWER

    def damage(self, actor):
        self.kill()
        super().damage(actor)

    def player_react(self, player):
        return

    def player_collide(self, player):
        return