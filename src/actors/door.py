
import pygame
from actors.actor import TileCollisionActor
from utils.resource_manager import ResourceManager

DOOR_MOVE_DURATION = 60
DOOR_POS_MAX = 16

class Door(TileCollisionActor):
    RENDER_PRIORITY = 0
    HITBOX_OFFSET = (0, 0)
    HITBOX_SIZE = (16, 16)

    def __init__(self, pos, rotation, dungeon):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,1).rotate(-rotation),
            speed=0)

        self.image = ResourceManager.load_image('door.png')
        self.image = pygame.transform.rotate(self.image, rotation)

        self.dungeon = dungeon

        self.moving = False
        self.move_offset = DOOR_POS_MAX
        self.pos_prev = self.pos


    def add_to_groups(self, room_context):
        super().add_to_groups(room_context)
        room_context.doors.add(self)

    def draw(self, screen):
        screen.blit(self.image, self.pos)
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)

    def update(self, time):
        # update door position
        if self.move_offset < DOOR_POS_MAX:
            self.move_offset += time * DOOR_POS_MAX / DOOR_MOVE_DURATION
            self.pos = self.pos_prev - self.dir * self.move_offset
        elif self.moving:
            # kill door if it reached the final position
            self.move_offset = DOOR_POS_MAX
            self.moving = False
            self.kill()

    def open(self):
        self.pos_prev = self.pos
        self.move_offset = 0
        self.moving = True
        self.dungeon.remove_collision_tile(self.get_tile_collision())

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return

    def player_collide(self, player):
        return


FINAL_DOOR_PLAYER_DISTANCE_MIN = 64

class FinalDoor(Door):

    def __init__(self, pos, rotation, dungeon):
        Door.__init__(self, pos, rotation, dungeon)

        self.image = ResourceManager.load_image('door_final.png')
        self.image = pygame.transform.rotate(self.image, rotation)
        self.sound = ResourceManager.load_sound('use_key.wav')

        self.player_has_key = False
        self.room_cleared = False
        self.opened = False

    def open(self):
        self.room_cleared = True
        if self.player_has_key:
            super().open()
            self.opened = True
            self.dungeon.player.use_key()
            self.sound.play()

    def player_react(self, player):
        if not self.opened:
            self.player_has_key = player.has_key
            dist = self.pos.distance_to(player.pos)
            if dist < FINAL_DOOR_PLAYER_DISTANCE_MIN and self.room_cleared:
                self.open()