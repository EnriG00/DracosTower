
import pygame
from actors.actor import DamageActor, TileCollisionActor
from utils.resource_manager import ResourceManager

# angle step between poses
ANGLE_STEP = 15

BEAM_LENGTH = 400

EYE_POS = [(13,18),(11,17),(9,17),(7,16),(5,15),(3,14),(2,12),(3,10),(5,9),(7,8),(9,7),(11,7),(13,6),(15,7),(17,7),(19,8),(21,9),(23,10),(24,12),(23,14),(21,15),(19,16),(17,17),(15,17)]
DRAW_FIRST = [True,True,True,True,True,True,True,False,False,False,False,False,False,False,False,False,False,False,True,True,True,True,True,True,]

LASER_STATUE_DAMAGE_POWER = 1


class LaserStatue(TileCollisionActor, DamageActor):
    RENDER_PRIORITY = 1

    HITBOX_OFFSET = (6,16)
    HITBOX_SIZE = (16,16)

    def __init__(self, pos, dungeon=None):
        super().__init__(
            pos=pygame.Vector2(pos),
            dir=pygame.Vector2(0,1),
            speed=0)

        self.image = ResourceManager.load_image('laser_statue.png')
        self.animation = ResourceManager.load_animation('laser_statue.json')

        self.beam_pos_start = EYE_POS[0]
        self.beam_pos_end = EYE_POS[0]


    def get_damage_power(self):
        return LASER_STATUE_DAMAGE_POWER


    def draw(self, screen):
        if DRAW_FIRST[self.animation.current_keyframe_index]:
            screen.blit(self.image, self.pos, self.animation.get_rect())
            pygame.draw.line(screen, (255,0,0), self.beam_pos_start, self.beam_pos_end, width=4)
            pygame.draw.line(screen, (255,127,0), self.beam_pos_start, self.beam_pos_end, width=2)
        else:
            pygame.draw.line(screen, (255,0,0), self.beam_pos_start, self.beam_pos_end, width=4)
            pygame.draw.line(screen, (255,127,0), self.beam_pos_start, self.beam_pos_end, width=2)
            screen.blit(self.image, self.pos, self.animation.get_rect())
        
        # debug
        #pygame.draw.rect(screen, (255,0,0), self.rect, width=1)


    def update(self, time):
        self.animation.update(time)
        self.dir = pygame.math.Vector2(0,1).rotate(self.animation.anim_counter / self.animation.animation_data.frame_count * 360)

        
    # check beam colliding with map
    def map_collide(self, map_collisions, time):
        # create long beam line
        self.beam_pos_start = self.pos + EYE_POS[self.animation.current_keyframe_index]
        self.beam_pos_end = self.beam_pos_start + self.dir * BEAM_LENGTH

        # find line intersection points
        positions = []
        for col_rect in map_collisions:
            positions.extend(col_rect.clipline(self.beam_pos_start, self.beam_pos_end))
        
        # discard self rect collision points
        for pos in self.rect.clipline(self.beam_pos_start, self.beam_pos_end):
            positions.remove(pos)

        # assign nearest point to line end position
        if len(positions) > 0:
            dist_array = [self.beam_pos_start.distance_to(pos) for pos in positions]
            self.beam_pos_end = positions[dist_array.index(min(dist_array))]


    def player_react(self, player):
        if len(player.rect.clipline(self.beam_pos_start, self.beam_pos_end)) > 0:
            self.damage(player)
        
    def player_collide(self, player):
        return