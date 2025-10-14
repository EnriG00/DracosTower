
from actors.bow_charge_observer import BowChargeObserver
from director import FRAME_TIME_DEFAULT, SCREEN_SIZE, UI_HEIGHT
from scene.dungeon.dungeon_ui import DungeonUI
from scene.dungeon.floor.floor import Floor
from actors.item import KeyItem
from scene.dungeon.pause import Pause
from scene.dungeon.floor.room import DOOR_POS_DOWN, DOOR_POS_LEFT, DOOR_POS_RIGHT, DOOR_POS_UP, ROOM_SIZE, ROOM_SIZE_SCREEN, TILE_SIZE
from scene.menu.die_screen import DieScreen
from scene.menu.win_screen import WinScreen
from scene.scene import Scene
from actors.player import Player
import sys
import pygame
from pygame.locals import *
from utils.controls import KEY_PAUSE

from utils.resource_manager import ResourceManager



FLOOR_TRANSITION_DURATION = 100
PLAYER_DIE_TRANSITION_DURATION = 150

SCROLL_DURATION = 60
# scroll moving step
SCROLL_STEP_X = ROOM_SIZE[0] * TILE_SIZE / SCROLL_DURATION
SCROLL_STEP_Y = ROOM_SIZE[1] * TILE_SIZE / SCROLL_DURATION

# player position when changing room
PLAYER_POS_UP = (128,32)
PLAYER_POS_LEFT = (32,80)
PLAYER_POS_RIGHT = (224,80)
PLAYER_POS_DOWN = (128,128)

# player default position (room center)
PLAYER_POS_DEFAULT = (128,80)


# transition effect mask
class TransitionMask:

    def __init__(self):
        self.mask = pygame.Surface(SCREEN_SIZE, depth=8)
        self.circle_radius = pygame.Vector2(SCREEN_SIZE).length() # screen diagonal
        self.circle_radius_dest = self.circle_radius
        self.circle_center = pygame.Vector2(SCREEN_SIZE) / 2 # screen center

        self.move_step = self.circle_radius / FLOOR_TRANSITION_DURATION
        self.growth_direction = 0

        self.enabled = False

    def update(self, time):
        self.circle_radius += min(self.move_step * time, abs(self.circle_radius_dest - self.circle_radius)) * self.growth_direction
        if self.circle_radius == self.circle_radius_dest:
            self.enabled = False

    def draw(self, screen):
        self.mask.fill((0,0,0))
        pygame.draw.circle(self.mask, (255,255,255), self.circle_center, self.circle_radius)
        screen.blit(self.mask, (0,0), special_flags=BLEND_MULT)

    def calculate_max_radius(self, center):
        center_pos = pygame.Vector2(center)
        return max(center_pos.distance_to((0,0)), center_pos.distance_to(SCREEN_SIZE))

    def open(self, center, duration):
        self.circle_center = center
        self.circle_radius = 0
        self.growth_direction = 1
        self.circle_radius_dest = self.calculate_max_radius(center)
        self.move_step = self.circle_radius_dest / duration
        self.enabled = True

    def close(self, center, duration):
        self.circle_center = center
        self.circle_radius = self.calculate_max_radius(center)
        self.growth_direction = -1
        self.circle_radius_dest = 0
        self.move_step = self.circle_radius / duration
        self.enabled = True


class Dungeon(Scene):

    def __init__(self, director):
        Scene.__init__(self, director)

        # load floor database
        self.floor_db = ResourceManager.load_floor_database()
        self.floor_count = len(self.floor_db)
        self.floor_index = 0

        # load secret room sound
        self.sound_secret = ResourceManager.load_sound('secret.wav')

        # create player
        self.player = Player(PLAYER_POS_DEFAULT, self)

        # init ui
        self.ui = DungeonUI()
        self.bow_charge_observer = BowChargeObserver()
        # add ui observers to player
        self.player.add_observer(self.ui.life_observer)
        self.player.add_observer(self.ui.bomb_stat)
        self.player.add_observer(self.ui.arrow_stat)
        self.player.add_observer(self.ui.attack_stat)
        self.player.add_observer(self.ui.speed_stat)
        self.player.add_observer(self.ui.key_observer)

        # update ui observer values
        self.player.notify_observers()

        # create floor
        self.setup_floor(self.floor_db[self.floor_index]["tileset"], self.floor_db[self.floor_index]["room_count"], self.floor_index)
        
        # create floor transition effect
        self.transition_mask = TransitionMask()
        # enable screen opening effect
        self.transition_mask.open(self.player.rect.center - self.current_room.global_pos + (0,UI_HEIGHT), FLOOR_TRANSITION_DURATION)
        
        # floor change state
        self.changing_floor = False
        self.skip_frame = True
        self.player_die_transition = False

        # load music
        ResourceManager.load_music('music_intro.mp3', queue=False)
        pygame.mixer.music.play(loops=0)
        ResourceManager.load_music('music_loop.mp3', queue=True)


    def setup_floor(self, tileset_name, floor_room_count, floor_index):
        # create floor
        self.floor = Floor(self, tileset_name, floor_room_count, floor_index)

        # set start room as current room
        self.current_room = self.floor.root_room
        # create dungeon drawing surface
        size_x, size_y = self.floor.size
        self.dungeon_surface = pygame.Surface((ROOM_SIZE[0] * TILE_SIZE * size_x, ROOM_SIZE[1] * TILE_SIZE * size_y))

        # create floor scrolling rectangle
        self.floor_view_rect = pygame.Rect(pygame.Vector2(self.current_room.pos).elementwise() * ROOM_SIZE_SCREEN, ROOM_SIZE_SCREEN)
        self.scroll_dest = self.floor_view_rect.topleft
        self.scroll_direction = pygame.Vector2(0,0)

        # add player to all room sprite groups
        for room in self.floor.rooms:
            self.player.add_to_groups(room.sprite_context)
            self.bow_charge_observer.add_to_groups(room.sprite_context)

            # add tile actors to room collisions
            for tile_actor in room.sprite_context.tile_collision_actors:
                room.collisions.append(tile_actor.get_tile_collision())

        # set player position in start room
        self.player.set_position(self.current_room.global_pos + PLAYER_POS_DEFAULT)

        # update floor map
        self.ui.floor_map.bind_floor(self.floor, self.current_room)


    def update(self, time):

        if self.skip_frame:
            self.skip_frame = False
            return

        # update transitions
        if self.transition_mask.enabled:
            self.transition_mask.update(time)
            return
        elif self.changing_floor:
            self.floor_index += 1

            # enable win screen when last floor is completed
            if self.floor_index == self.floor_count:
                self.director.switch_scene(WinScreen(self.director))
                return

            # create next floor
            self.setup_floor(self.floor_db[self.floor_index]["tileset"], self.floor_db[self.floor_index]["room_count"], self.floor_index)
            self.changing_floor = False
            # enable transition effect
            self.transition_mask.open(self.player.rect.center - self.current_room.global_pos + (0,UI_HEIGHT), FLOOR_TRANSITION_DURATION)
            # skip next frame to play transition effect correctly
            self.skip_frame = True
            return
        elif self.player_die_transition:
            self.director.switch_scene(DieScreen(self.director))
            return

        # check scroll
        if self.is_scrolling():
            # update scroll
            self.floor_view_rect.left += min(SCROLL_STEP_X * time, abs(self.scroll_dest.x - self.floor_view_rect.left)) * self.scroll_direction.x
            self.floor_view_rect.top += min(SCROLL_STEP_Y * time, abs(self.scroll_dest.y - self.floor_view_rect.top)) * self.scroll_direction.y
            # don't update actors until scroll is finished
            return

        # AI
        for actor in self.current_room.sprite_context.updatable_actors:
            actor.player_react(self.player)

        # update actors
        self.current_room.sprite_context.updatable_actors.update(time)

        # actor vs room collisions
        for actor in self.current_room.sprite_context.updatable_actors:
            actor.map_collide(self.current_room.collisions, time)

        # actor vs player collisions
        for actor in pygame.sprite.spritecollide(self.player, self.current_room.sprite_context.updatable_actors, dokill=False):
            actor.player_collide(self.player)

        # player attacks vs enemies collisions
        for player_attack, enemies in pygame.sprite.groupcollide(self.current_room.sprite_context.player_attacks, self.current_room.sprite_context.enemies, False, False).items():
            for enemy in enemies:
                player_attack.damage(enemy)

        # activate room scrolling if player gets outside view rectangle
        if not self.floor_view_rect.colliderect(self.player.rect):
            # check room scrolling direction
            if (abs(self.floor_view_rect.centerx - self.player.rect.centerx) > abs(self.floor_view_rect.centery - self.player.rect.centery)):
                if (self.floor_view_rect.centerx < self.player.rect.centerx):
                    # right
                    self.current_room = self.current_room.right
                    self.player.set_position(self.current_room.global_pos + PLAYER_POS_LEFT)
                    self.enable_scroll(1,0)
                else:
                    # left
                    self.current_room = self.current_room.left
                    self.player.set_position(self.current_room.global_pos + PLAYER_POS_RIGHT)
                    self.enable_scroll(-1,0)
            else:
                if (self.floor_view_rect.centery < self.player.rect.centery):
                    # down
                    self.current_room = self.current_room.down
                    self.player.set_position(self.current_room.global_pos + PLAYER_POS_UP)
                    self.enable_scroll(0,1)
                else:
                    # up
                    self.current_room = self.current_room.up
                    self.player.set_position(self.current_room.global_pos + PLAYER_POS_DOWN)
                    self.enable_scroll(0,-1)

            # update room state
            self.floor.explore_room(self.current_room)
            # update ui
            self.ui.floor_map.set_current_room(self.current_room)
        

    def is_scrolling(self):
        return self.floor_view_rect.topleft != self.scroll_dest

    def enable_scroll(self, dir_x, dir_y):
        self.scroll_direction = pygame.Vector2(dir_x, dir_y)
        self.scroll_dest = self.floor_view_rect.topleft + self.scroll_direction.elementwise() * ROOM_SIZE_SCREEN

    
    def change_floor(self):
        if self.floor_index+1 == self.floor_count:
            pygame.mixer.music.fadeout(int(FLOOR_TRANSITION_DURATION * FRAME_TIME_DEFAULT))
        # enable floor transition
        self.changing_floor = True
        self.transition_mask.close(self.player.rect.center - self.current_room.global_pos + (0,UI_HEIGHT), FLOOR_TRANSITION_DURATION)


    def events(self, event_list):
        for event in event_list:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == KEY_PAUSE and not self.is_scrolling() and not self.transition_mask.enabled:
                self.director.push_scene(Pause(self.director))
                self.skip_frame = True

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if not self.is_scrolling() and not self.transition_mask.enabled:
            self.player.process_input(pressed_keys)


    def draw(self, screen):
        
        # draw floor bottom layer
        self.floor.draw_bottom(self.dungeon_surface)

        # draw priority 0 actors
        for actor in self.current_room.sprite_context.tile_layer_actors:
            actor.draw(self.dungeon_surface)

        # draw priority 1 actors
        for actor in sorted(self.current_room.sprite_context.bottom_layer_actors, key=lambda x: x.rect.top):
            actor.draw(self.dungeon_surface)

        # draw floor top layer
        self.floor.draw_top(self.dungeon_surface)

        # draw priority 2 actors
        for actor in sorted(self.current_room.sprite_context.top_layer_actors, key=lambda x: x.rect.top):
            actor.draw(self.dungeon_surface)

        # draw ui
        for actor in self.current_room.sprite_context.ui_layer:
            actor.draw(self.dungeon_surface)
        screen.blit(self.dungeon_surface, (0,UI_HEIGHT), self.floor_view_rect)
        self.ui.draw(screen)

        # apply transition mask
        if self.transition_mask.enabled or self.changing_floor or self.player_die_transition:
            self.transition_mask.draw(screen)


    def add_actor(self, actor):
        actor.add_to_groups(self.current_room.sprite_context)

    def complete_room(self):
        if self.current_room.has_key:
            # create key item
            key_pos = self.current_room.get_key_spawn_position()
            key = KeyItem(key_pos)
            key.add_to_groups(self.current_room.sprite_context)
        # open doors
        for door in self.current_room.sprite_context.doors:
            door.open()


    def exit(self):
        pygame.mixer.music.stop()
        self.player_die_transition = True
        self.transition_mask.close(self.player.rect.center - self.current_room.global_pos + (0,UI_HEIGHT), PLAYER_DIE_TRANSITION_DURATION)

    def remove_collision_tile(self, tile):
        self.current_room.collisions.remove(tile)

    def break_wall(self, wall_tile):
        local_pos = pygame.Vector2(wall_tile.topleft) - self.current_room.global_pos
        # check wall side and room neighbour type
        if local_pos == DOOR_POS_UP and self.current_room.up is not None and (self.current_room.up.type == 'SECRET' or self.current_room.type == 'SECRET'):
            # update door tiles
            self.current_room.update_door_up('SECRET')
            self.current_room.up.update_door_down('SECRET')
            # remove wall collision in secret room
            secret_room = self.current_room.up
            secret_room.remove_wall(DOOR_POS_DOWN)
        elif local_pos == DOOR_POS_LEFT and self.current_room.left is not None and (self.current_room.left.type == 'SECRET' or self.current_room.type == 'SECRET'):
            # update door tiles
            self.current_room.update_door_left('SECRET')
            self.current_room.left.update_door_right('SECRET')
            # remove wall collision in secret room
            secret_room = self.current_room.left
            secret_room.remove_wall(DOOR_POS_RIGHT)
        elif local_pos == DOOR_POS_RIGHT and self.current_room.right is not None and (self.current_room.right.type == 'SECRET' or self.current_room.type == 'SECRET'):
            # update door tiles
            self.current_room.update_door_right('SECRET')
            self.current_room.right.update_door_left('SECRET')
            # remove wall collision in secret room
            secret_room = self.current_room.right
            secret_room.remove_wall(DOOR_POS_LEFT)
        elif local_pos == DOOR_POS_DOWN and self.current_room.down is not None and (self.current_room.down.type == 'SECRET' or self.current_room.type == 'SECRET'):
            # update door tiles
            self.current_room.update_door_down('SECRET')
            self.current_room.down.update_door_up('SECRET')
            # remove wall collision in secret room
            secret_room = self.current_room.down
            secret_room.remove_wall(DOOR_POS_UP)
        else:
            return

        # remove wall collision tile from current room
        self.current_room.collisions.remove(wall_tile)
        
        # repaint rooms in floor surface
        self.floor.update_room_surface(self.current_room)
        self.floor.update_room_surface(secret_room)

        # play secret room sound
        self.sound_secret.play()

