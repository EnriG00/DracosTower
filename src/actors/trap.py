import pygame
from actors.actor import DamageActor
from scene.dungeon.floor.collisions import COL_NONE
from utils.resource_manager import ResourceManager

TRAP_SPEED = 2
TRAP_PLAYER_DETECTION_RECT_LENGTH_X = 192
TRAP_PLAYER_DETECTION_RECT_LENGTH_Y = 96

TRAP_DAMAGE_POWER = 1

class Trap(DamageActor):
    RENDER_PRIORITY = 1

    HITBOX_OFFSET = (0,0)
    HITBOX_SIZE = (16,16)

    def __init__(self, pos, dungeon=None):
        super().__init__(pygame.Vector2(pos), dir=pygame.Vector2(0,0), speed=0)

        self.image = ResourceManager.load_image('trap.png')

        self.player_detection_rect_up = pygame.Rect(pos, (self.HITBOX_SIZE[0],TRAP_PLAYER_DETECTION_RECT_LENGTH_Y))
        self.player_detection_rect_left = pygame.Rect(pos, (TRAP_PLAYER_DETECTION_RECT_LENGTH_X,self.HITBOX_SIZE[1]))
        self.player_detection_rect_right = pygame.Rect(pos, (TRAP_PLAYER_DETECTION_RECT_LENGTH_X,self.HITBOX_SIZE[1]))
        self.player_detection_rect_down = pygame.Rect(pos, (self.HITBOX_SIZE[0],TRAP_PLAYER_DETECTION_RECT_LENGTH_Y))
        self.align_rects()

    def draw(self, screen):
        screen.blit(self.image, self.pos)
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)
        #pygame.draw.rect(screen, (0,0,255), self.player_detection_rect_up, width=1)
        #pygame.draw.rect(screen, (0,0,255), self.player_detection_rect_left, width=1)
        #pygame.draw.rect(screen, (0,0,255), self.player_detection_rect_right, width=1)
        #pygame.draw.rect(screen, (0,0,255), self.player_detection_rect_down, width=1)

    def get_damage_power(self):
        return TRAP_DAMAGE_POWER

    def player_collide(self, player):
        self.damage(player)

    def align_rects(self):
        self.player_detection_rect_up.bottomleft = self.rect.topleft
        self.player_detection_rect_left.topright = self.rect.topleft
        self.player_detection_rect_right.topleft = self.rect.topright
        self.player_detection_rect_down.topleft = self.rect.bottomleft

    def move(self, offset):
        super().move(offset)
        self.align_rects()

    def update(self, time):
        self.move(self.dir * self.speed * time)

    def player_react(self, player):
        # check trap is not moving
        if self.speed == 0:
            # detect player
            if player.rect.colliderect(self.player_detection_rect_up):
                self.dir.xy = 0, -1
            elif player.rect.colliderect(self.player_detection_rect_left):
                self.dir.xy = -1, 0
            elif player.rect.colliderect(self.player_detection_rect_right):
                self.dir.xy = 1, 0
            elif player.rect.colliderect(self.player_detection_rect_down):
                self.dir.xy = 0, 1
            else:
                return
            # enable trap movement
            self.speed = TRAP_SPEED


    def map_collide(self, map_collisions, time):
        index = self.rect.collidelist(map_collisions)

        if index != -1:
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
                # stop moving
                self.speed = 0



