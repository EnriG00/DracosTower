import pygame
from actors.actor import DamageActor
from scene.dungeon.floor.collisions import COL_BREAKABLE_WALL
from utils.resource_manager import ResourceManager


EXPLOSION_DAMAGE_POWER = 2


class Explosion(DamageActor):
    RENDER_PRIORITY = 1

    HITBOX_OFFSET = (7,7)
    HITBOX_SIZE = (32,32)

    def __init__(self, dungeon, pos):
        super().__init__(pygame.Vector2(pos), dir=pygame.Vector2(0,0), speed=0)

        self.image = ResourceManager.load_image('explosion.png')
        self.animation = ResourceManager.load_animation('explosion.json')
        self.sound = ResourceManager.load_sound('explosion.wav')

        self.dungeon = dungeon

        self.sound.play()


    def draw(self, screen):
        screen.blit(self.image, self.pos, self.animation.get_rect())
        # debug
        #pygame.draw.rect(screen, (255,0,0),self.rect, width=1)

    def update(self, time):
        self.animation.update(time)
        if (self.animation.ended()):
            self.kill()

    def map_collide(self, map_collisions, time):
        for index in self.rect.collidelistall(map_collisions):
            tile = map_collisions[index]
            if (tile.type == COL_BREAKABLE_WALL):
                self.dungeon.break_wall(tile)

    def add_to_groups(self, room_context):
        super().add_to_groups(room_context)
        room_context.player_attacks.add(self)

    def get_damage_power(self):
        return EXPLOSION_DAMAGE_POWER

    def player_collide(self, player):
        self.damage(player)

    def player_react(self, player):
        return