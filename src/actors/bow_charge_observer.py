import pygame
from actors.actor import Actor
from actors.player import PLAYER_BOW_CHARGE_MIN


BOW_CHARGE_BAR_POSITION = (5,5)
BOW_CHARGE_SIZE = (24,4)
BOW_CHARGE_PLAYER_OFFSET = (13,0)
BOW_CHARGE_ALPHA = 191
BOW_CHARGE_BAR_COLOR_PROGRESS = (31,255,112)
BOW_CHARGE_BAR_COLOR_FULL = (255,0,0)

class BowChargeObserver(Actor):
    RENDER_PRIORITY = 3

    def __init__(self):
        super().__init__()

        self.bar_surface = pygame.Surface((BOW_CHARGE_SIZE[0]+2,BOW_CHARGE_SIZE[1]+2))
        # border
        self.bar_surface.fill((0,0,0))
        # background
        self.bar_surface.fill((31,92,112), pygame.Rect((1,1),(BOW_CHARGE_SIZE)))
        # progress rectangle
        self.progress_rect = pygame.Rect((1,1),(0,BOW_CHARGE_SIZE[1]))
        # position in screen
        self.pos = pygame.Vector2(BOW_CHARGE_BAR_POSITION)
        self.rect = pygame.Rect(self.pos, pygame.Vector2(BOW_CHARGE_SIZE).elementwise() + 2)

        self.bar_color = BOW_CHARGE_BAR_COLOR_PROGRESS
        self.hide = True

    def draw(self, screen):
        if (not self.hide):
            # fill background
            self.bar_surface.fill((31,92,112), pygame.Rect((1,1),(BOW_CHARGE_SIZE)))
            # fill bar
            self.bar_surface.fill(self.bar_color, self.progress_rect)
            # set alpha
            self.bar_surface.set_alpha(BOW_CHARGE_ALPHA)
            screen.blit(self.bar_surface, self.pos)


    def player_react(self, player):
        self.hide = player.bow_charge == 0
        if self.hide:
            return

        # set bar size and color
        if (player.bow_charge < PLAYER_BOW_CHARGE_MIN):
            self.progress_rect.width = int(player.bow_charge/PLAYER_BOW_CHARGE_MIN*BOW_CHARGE_SIZE[0])
            self.bar_color = BOW_CHARGE_BAR_COLOR_PROGRESS
        else:
            self.progress_rect.width = BOW_CHARGE_SIZE[0]
            self.bar_color = BOW_CHARGE_BAR_COLOR_FULL

        # set bar position
        self.pos = player.pos + BOW_CHARGE_PLAYER_OFFSET

    def update(self, time):
        return

    def map_collide(self, map_collisions, time):
        return
    
    def player_collide(self, player):
        return