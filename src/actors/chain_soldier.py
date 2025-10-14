import pygame
from actors.actor import Actor, DamageActor
from actors.enemy import Enemy
from scene.dungeon.floor.collisions import COL_NONE
from utils.resource_manager import ResourceManager


SPIKE_BALL_DAMAGE_POWER = 1

CHAIN_SOLDIER_SPIKE_BALL_DISTANCE = 32
CHAIN_SOLDIER_SPIKE_BALL_ROTATE_SPEED = 3
CHAIN_SOLDIER_CHAIN_COUNT = 4

CHAIN_SOLDIER_HAND_OFFSET = (25,10)
CHAIN_SOLDIER_SPEED = .4

CHAIN_SOLDIER_LIFE = 4
CHAIN_SOLDIER_DAMAGE_POWER = 1


class SpikeBall(DamageActor):
    RENDER_PRIORITY = 2
    HITBOX_OFFSET = (1,1)
    HITBOX_SIZE = (14,14)

    def __init__(self, pos):
        Actor.__init__(self,
            pygame.Vector2(pos),
            pygame.Vector2(0,0),
            0
            )

        self.image = ResourceManager.load_image('spike_ball.png')


    def draw(self, screen):
        screen.blit(self.image, self.pos)
        # debug
        #pygame.draw.rect(screen, (255,0,0),self.rect, width=1)

    def update(self, time):
        # spike ball is updated by ChainSoldier parent
        return

    def set_hitbox_position(self, pos):
        self.rect.center = pos
        self.pos = pos - self.image.get_rect().center

    def get_damage_power(self):
        return SPIKE_BALL_DAMAGE_POWER

    def player_collide(self, player):
        self.damage(player)

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return




class ChainSoldier(Enemy):
    RENDER_PRIORITY = 1
    DROP_CHANCE = .9
    HITBOX_OFFSET = (8,12)
    HITBOX_SIZE = (16,16)
    DAMAGE_COOLDOWN = 60

    def __init__(self, pos, dungeon):
        super().__init__(
            pos=pos,
            dir=(0,0),
            speed=CHAIN_SOLDIER_SPEED,
            life=CHAIN_SOLDIER_LIFE)

        self.image = ResourceManager.load_image('chain_soldier.png')
        self.animation = ResourceManager.load_animation('chain_soldier.json')
        
        self.spike_ball_chain_image = ResourceManager.load_image('spike_ball_chain.png')
        self.chain_offset = self.spike_ball_chain_image.get_rect().center

        self.dungeon = dungeon

        self.hand_pos = self.pos + CHAIN_SOLDIER_HAND_OFFSET

        self.spike_ball = SpikeBall(pos)
        self.spike_ball_dir = pygame.Vector2(1,0)
        self.spike_ball_dir.scale_to_length(CHAIN_SOLDIER_SPIKE_BALL_DISTANCE)
        self.spike_ball.set_hitbox_position(self.hand_pos + self.spike_ball_dir)



    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, self.pos, self.animation.get_rect())
        for i in range(CHAIN_SOLDIER_CHAIN_COUNT):
            screen.blit(self.spike_ball_chain_image, self.hand_pos + self.spike_ball_dir * i / CHAIN_SOLDIER_CHAIN_COUNT - self.chain_offset)
        # debug
        #pygame.draw.line(screen, (0,255,0), self.rect.center, self.dir * 32 + self.rect.center)
        #pygame.draw.rect(screen, (255,0,0),self.rect, width=1)
        #pygame.draw.line(screen, (0,255,0), self.hand_pos, self.hand_pos + self.spike_ball_dir)

    def move(self, offset):
        super().move(offset)
        self.hand_pos = self.pos + CHAIN_SOLDIER_HAND_OFFSET
        self.spike_ball.set_hitbox_position(self.hand_pos + self.spike_ball_dir)

    def update(self, time):
        super().update(time)

        self.spike_ball_dir.rotate_ip(CHAIN_SOLDIER_SPIKE_BALL_ROTATE_SPEED * time)
        self.move(self.dir * self.speed * time)
        self.animation.update(time)

    def player_react(self, player):
        self.dir = (player.pos - self.pos).normalize()

    def add_to_groups(self, room_context):
        super().add_to_groups(room_context)
        self.spike_ball.add_to_groups(room_context)


    def get_damage_power(self):
        return CHAIN_SOLDIER_DAMAGE_POWER

    def die(self):
        self.spike_ball.kill()
        super().die()

    def map_collide(self, map_collisions, time):
        for index in self.rect.collidelistall(map_collisions):
            tile = map_collisions[index]
            if (tile.type != COL_NONE):
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

    


