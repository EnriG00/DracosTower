
import pygame
from director import SCREEN_WIDTH, UI_HEIGHT
from utils.resource_manager import ResourceManager

UI_RECT = pygame.Rect((0, 0), (SCREEN_WIDTH, UI_HEIGHT))

NUMBER_FONT_RECT_WIDTH = 7
NUMBER_FONT_RECT_HEIGHT = 8
NUMBER_FONT_RECT_SIZE = (NUMBER_FONT_RECT_WIDTH, NUMBER_FONT_RECT_HEIGHT)

LIFE_TEXT_POS = (9,5)
LIFE_HEART_POS = (8,18)
LIFE_HEART_WIDTH = 7

STAT_OBSERVER_POS_FIRST = 60
STAT_OBSERVER_WIDTH = 24
STAT_OBSERVER_ICON_OFFSET = (4, 1)
STAT_OBSERVER_FONT_POS = (5, 20)

KEY_ICON_POS = (159,8)

FLOOR_TEXT_POS = (180,12)
FLOOR_INDEX_POS = (212,12)
MAP_FRAME_POS = (223,0)
MAP_ROOM_SIZE = 4
MAP_POS = (225,3)
MAP_SIZE = (44,26)

MAP_ROOM_COLOR_VISITED = (255,255,255)
MAP_ROOM_COLOR_VISIBLE = (111,111,111)


class PlayerStatObserver:

    def notify(self, player):
        raise NotImplemented("'notify' method must be implemented")


class PlayerStatUI(PlayerStatObserver):

    def __init__(self, icon, number_font, value_default, pos, value_to_int):
        pygame.sprite.Sprite.__init__(self)

        self.value = value_default

        self.icon = icon
        self.number_font = number_font
        self.value_to_int = value_to_int
        self.update_digits()

        self.pos = pygame.Vector2(pos)
        self.icon_pos = (self.pos + STAT_OBSERVER_ICON_OFFSET)

    def update_digits(self):
        str_value = "{:02d}".format(self.value_to_int(self.value))
        self.left_digit = int(str_value[0])
        self.right_digit = int(str_value[1])

    def draw(self, screen):
        screen.blit(self.icon, self.icon_pos)
        screen.blit(self.number_font[self.left_digit], self.pos + STAT_OBSERVER_FONT_POS)
        screen.blit(self.number_font[self.right_digit], self.pos + STAT_OBSERVER_FONT_POS + (NUMBER_FONT_RECT_WIDTH,0))


class BombStat(PlayerStatUI):

    def __init__(self, number_font, value, pos):
        super().__init__(ResourceManager.load_image('item_bomb.png'), number_font, value, pos, lambda x : x)

    def notify(self, player):
        self.value = player.bomb_count
        self.update_digits()


class ArrowStat(PlayerStatUI):

    def __init__(self, number_font, value, pos):
        super().__init__(ResourceManager.load_image('item_arrow.png'), number_font, value, pos, lambda x : x)

    def notify(self, player):
        self.value = player.arrow_count
        self.update_digits()


class AttackStat(PlayerStatUI):

    def __init__(self, number_font, value, pos):
        super().__init__(ResourceManager.load_image('item_sword.png'), number_font, value, pos, lambda x : int(x * 2))

    def notify(self, player):
        self.value = player.attack_power
        self.update_digits()


class SpeedStat(PlayerStatUI):

    def __init__(self, number_font, value, pos):
        super().__init__(ResourceManager.load_image('item_speed.png'), number_font, value, pos, lambda x : int(x * 8))

    def notify(self, player):
        self.value = player.speed_improvement
        self.update_digits()


class PlayerLifeObserver(PlayerStatObserver):

    def __init__(self, value):
        super(PlayerLifeObserver, self).__init__()

        self.text_image = ResourceManager.load_image('ui_life.png')
        self.heart_image = ResourceManager.load_image('ui_heart.png')
    
    def draw(self, screen):
        screen.blit(self.text_image, LIFE_TEXT_POS)
        for i in range(self.value):
            screen.blit(self.heart_image, (LIFE_HEART_POS[0] + LIFE_HEART_WIDTH * i + i, LIFE_HEART_POS[1]))

    def notify(self, player):
        self.value = player.life


class FloorMap:

    def __init__(self, number_font):
        pygame.sprite.Sprite.__init__(self)
        self.number_font = number_font
        self.floor_text_image = ResourceManager.load_image('ui_floor.png')
        self.map_frame_image = ResourceManager.load_image('ui_map_frame.png')

        # create scrolling rectangle
        self.map_scroll_rect = pygame.Rect((0,0), MAP_SIZE)


    def bind_floor(self, floor, current_room):
        self.floor = floor
        self.current_room = current_room

        # create map drawing surface
        size_x, size_y = floor.size
        self.map_surface = pygame.Surface((1 + size_x * (MAP_ROOM_SIZE-1), 1 + size_y * (MAP_ROOM_SIZE-1)))

        self.update_map()
        self.update_scroll()

    # draw map in map surface
    def update_map(self):
        self.map_surface.fill((0,0,0))
        for visible_room in self.floor.visible_rooms:
            pos_x, pos_y = visible_room.pos
            pygame.draw.rect(self.map_surface, MAP_ROOM_COLOR_VISIBLE, (pos_x * (MAP_ROOM_SIZE-1), pos_y * (MAP_ROOM_SIZE-1), MAP_ROOM_SIZE, MAP_ROOM_SIZE), width=1)

        for visited_room in self.floor.visited_rooms:
            pos_x, pos_y = visited_room.pos
            pygame.draw.rect(self.map_surface, MAP_ROOM_COLOR_VISITED, (pos_x * (MAP_ROOM_SIZE-1), pos_y * (MAP_ROOM_SIZE-1), MAP_ROOM_SIZE, MAP_ROOM_SIZE), width=1)

        pygame.draw.rect(self.map_surface, (255,0,0), (self.current_room.pos[0] * (MAP_ROOM_SIZE-1)+1, self.current_room.pos[1] * (MAP_ROOM_SIZE-1)+1, MAP_ROOM_SIZE-2, MAP_ROOM_SIZE-2))

    def update_scroll(self):
        self.map_scroll_rect.center = self.current_room.pos[0] * (MAP_ROOM_SIZE-1) + int(MAP_ROOM_SIZE/2), self.current_room.pos[1] * (MAP_ROOM_SIZE-1) + int(MAP_ROOM_SIZE/2)

    def set_current_room(self, room):
        self.current_room = room
        self.update_map()
        self.update_scroll()

    def draw(self, screen):
        screen.blit(self.floor_text_image, FLOOR_TEXT_POS)
        screen.blit(self.number_font[self.floor.index+1], FLOOR_INDEX_POS)
        screen.blit(self.map_surface, MAP_POS, self.map_scroll_rect)
        screen.blit(self.map_frame_image, MAP_FRAME_POS)


class PlayerKeyObserver(PlayerStatObserver):

    def __init__(self):
        super(PlayerKeyObserver, self).__init__()

        self.image = ResourceManager.load_image('item_key.png')
        self.value = False # player_has_key

    def draw(self, screen):
        if self.value:
            screen.blit(self.image, KEY_ICON_POS)

    def notify(self, player):
        self.value = player.has_key


class DungeonUI:

    def __init__(self):
        # load number font
        number_font_image = ResourceManager.load_image('number_font.png')
        number_font = []
        for i in range(10):
            number_font.append(number_font_image.subsurface((NUMBER_FONT_RECT_WIDTH * i, 0), NUMBER_FONT_RECT_SIZE))

        # create stat observers
        self.bomb_stat = BombStat(number_font, 3, (STAT_OBSERVER_POS_FIRST,0))
        self.arrow_stat = ArrowStat(number_font, 5, (STAT_OBSERVER_POS_FIRST + STAT_OBSERVER_WIDTH,0))
        self.attack_stat = AttackStat(number_font, 1, (STAT_OBSERVER_POS_FIRST + STAT_OBSERVER_WIDTH * 2,0))
        self.speed_stat = SpeedStat(number_font, 1, (STAT_OBSERVER_POS_FIRST + STAT_OBSERVER_WIDTH * 3,0))
            
        self.key_observer = PlayerKeyObserver()
        self.life_observer = PlayerLifeObserver(3)

        # create map
        self.floor_map = FloorMap(number_font)


    def draw(self, screen):
        screen.fill((0, 0, 0), rect=UI_RECT)
        self.life_observer.draw(screen)
        self.bomb_stat.draw(screen)
        self.arrow_stat.draw(screen)
        self.attack_stat.draw(screen)
        self.speed_stat.draw(screen)
        self.key_observer.draw(screen)
        self.floor_map.draw(screen)
