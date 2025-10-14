
import pygame

# collision types
COL_NONE           = 0   # ground. no collision
COL_SOLID          = 1   # used for blocks, doesn't affect flying enemies or projectiles
COL_BREAKABLE      = 2   # solid, but breakable with bombs
COL_WALL           = 3   # used for walls, affects all entities
COL_DOOR           = 4   # unused
COL_BREAKABLE_WALL = 5   # used for secret room walls


class TileCollision(pygame.Rect):

    def __init__(self, pos, size, col_type):
        pygame.Rect.__init__(self,pos,size)
        self.type = col_type

    def __eq__(self, other):
        return (isinstance(other, type(self))
                and (self.topleft, self.size, self.type) ==
                    (other.topleft, other.size, other.type))

    def __hash__(self):
        return hash((self.topleft, self.size, self.type))
