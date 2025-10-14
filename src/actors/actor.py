
import pygame

from scene.dungeon.floor.collisions import COL_SOLID, TileCollision
from utils.resource_manager import ResourceManager


# updatable actor
class Actor(pygame.sprite.Sprite):
    RENDER_PRIORITY = -1
    HITBOX_OFFSET = (0,0)
    HITBOX_SIZE = (16,16)

    def __init__(self, pos=(0,0), dir=(0,0), speed=0):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.Vector2(pos) - self.HITBOX_OFFSET
        self.dir = pygame.Vector2(dir)
        self.speed = speed
        self.rect = pygame.Rect(pos,self.HITBOX_SIZE)

    def add_to_groups(self, room_context):
        room_context.updatable_actors.add(self)

        if self.RENDER_PRIORITY == 0:
            room_context.tile_layer_actors.add(self)
        elif self.RENDER_PRIORITY == 1:
            room_context.bottom_layer_actors.add(self)
        elif self.RENDER_PRIORITY == 2:
            room_context.top_layer_actors.add(self)
        elif self.RENDER_PRIORITY == 3:
            room_context.ui_layer.add(self)

    def update(self, time):
        raise NotImplemented("'update' method must be implemented")

    def player_react(self, player):
        raise NotImplemented("'player_react' method must be implemented")

    def map_collide(self, map_collisions, time):
        raise NotImplemented("'map_collide' method must be implemented")

    def player_collide(self, player):
        raise NotImplemented("'player_collide' method must be implemented")

    def move(self, offset):
        self.pos += offset
        self.rect.topleft = self.pos + self.HITBOX_OFFSET

    def set_position(self, pos):
        self.rect.topleft = pos
        self.pos = pos - self.HITBOX_OFFSET



# actor causing damage to other actors
class DamageActor(Actor):

    def get_damage_power(self):
        raise NotImplemented("'get_damage_power' method must be implemented")

    def damage(self, actor):
        actor.take_damage(self.get_damage_power())


# actor which can take damage
class LifeActor(Actor):
    DAMAGE_BLINKING_DELAY = 4

    def __init__(self, pos, dir, speed, life):
        super(LifeActor, self).__init__(pos,dir,speed)
        self.life = life
        # blinking effect
        self.damage_cooldown = 0
        self.hidden = False
        
        self.sound_hit = ResourceManager.load_sound('enemy_hit.wav')

    def take_damage(self, life_count):
        if self.damage_cooldown == 0:
            self.life -= life_count
            if self.life <= 0:
                self.die()
            self.damage_cooldown = self.DAMAGE_COOLDOWN
            self.sound_hit.play()

    def die(self):
        self.kill()

    def update(self, time):
        # update damage cooldown
        if (self.damage_cooldown > 0):
            self.damage_cooldown = max(self.damage_cooldown - time, 0)
        # update blinking effect
        self.hidden = (self.damage_cooldown % (self.DAMAGE_BLINKING_DELAY * 2)) > self.DAMAGE_BLINKING_DELAY


# actor with solid collision
class TileCollisionActor(Actor):
    
    def add_to_groups(self, room_context):
        super().add_to_groups(room_context)
        room_context.tile_collision_actors.add(self)

    def get_tile_collision(self):
        return TileCollision(self.rect.topleft, self.rect.size, COL_SOLID)

