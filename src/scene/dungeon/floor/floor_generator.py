
import random
from scene.dungeon.floor.room import Room
from utils.utils import *

FINAL_ROOM_MIN_DISTANCE = 3


# room position node
class RoomNode:

    def __init__(self, pos, depth):
        self.pos = pos
        self.depth = depth

    def get_neighbours(self):
        return [
            RoomNode((self.pos[0]-1, self.pos[1]), self.depth + 1), # left
            RoomNode((self.pos[0]+1, self.pos[1]), self.depth + 1), # right
            RoomNode((self.pos[0], self.pos[1]-1), self.depth + 1), # up
            RoomNode((self.pos[0], self.pos[1]+1), self.depth + 1), # down
            ]

    def get_probability(self):
        return self.depth

    def __repr__(self):
        return str(self.pos)
    def __eq__(self, other):
        if isinstance(other, RoomNode):
            return self.pos == other.pos
        else:
            return False
    def __ne__(self, other):
        return (not self.__eq__(other))
    def __hash__(self):
        return hash(self.__repr__())


class FloorGenerator:

    @staticmethod
    def __select_room(rooms):
        room_list = list(rooms)
        room_probability = []
        for room in room_list:
            room_probability.append(room.get_probability())
        
        return random.choices(room_list, room_probability)[0]


    # link new room to his neighbours
    @staticmethod
    def __link_room(room_dict, new_room):
        pos = new_room.pos

        # possible neighbour positions
        pos_left = position_left(pos)
        pos_right = position_right(pos)
        pos_up = position_up(pos)
        pos_down = position_down(pos)

        # link neighbours
        if (pos_up in room_dict):
            new_room.up = room_dict[pos_up]
            room_dict[pos_up].down = new_room
        if (pos_left in room_dict):
            new_room.left = room_dict[pos_left]
            room_dict[pos_left].right = new_room
        if (pos_right in room_dict):
            new_room.right = room_dict[pos_right]
            room_dict[pos_right].left = new_room
        if (pos_down in room_dict):
            new_room.down = room_dict[pos_down]
            room_dict[pos_down].up = new_room


    @staticmethod
    def __create_room_positions(room_count):
        # create root node
        root_node = RoomNode((0, 0), 0)
        room_positions = []
        room_positions.append(root_node.pos)

        # initialize frontier with root neighbours
        frontier = set()
        frontier.update(root_node.get_neighbours())

        # create room position nodes
        for i in range(room_count):
            # select new room from frontier
            new_room = FloorGenerator.__select_room(frontier)
            room_positions.append(new_room.pos)
            frontier.remove(new_room)

            # add new room neighbours to frontier
            for neighbour in new_room.get_neighbours():
                if (not neighbour.pos in room_positions):
                    frontier.add(neighbour)

        return room_positions


    @staticmethod
    def generate_floor(room_count):
        
        # generate room positions
        room_positions = FloorGenerator.__create_room_positions(room_count)

        # create and link rooms
        root_room = Room((0, 0), type='START')
        room_dict = {} # rooms indexed by position
        room_dict[(0, 0)] = root_room
        for i in range(1, len(room_positions)):
            new_room = Room(room_positions[i], type='COMMON')
            room_dict[new_room.pos] = new_room
            FloorGenerator.__link_room(room_dict, new_room)

        room_list = list(room_dict.values())


        # select final room
        final_room_candidates = []
        for room in room_list:
            # find distant rooms which have only 1 neighbour
            dist = room.get_distance()
            neighbour_count = room.get_neighbour_count()
            if (neighbour_count == 1 and dist > FINAL_ROOM_MIN_DISTANCE):
                final_room_candidates.append(room)

        if final_room_candidates:
            final_room = random.choice(final_room_candidates)
        else:
            # find free positions with only 1 neighbour
            final_room_candidates = []
            invalid_positions = []
            for room in room_list:
                for neighbour in room.get_free_neighbour_positions():
                    if (neighbour in final_room_candidates):
                        final_room_candidates.remove(neighbour)
                        invalid_positions.append(neighbour)
                    elif (neighbour not in invalid_positions):
                        final_room_candidates.append(neighbour)

            # get most distant position from candidates
            final_room_candidates.sort(key=distance_to_origin, reverse=True)
            final_room_pos = final_room_candidates[0]

            # link room
            if (position_up(final_room_pos) in room_dict):
                final_room = room_dict[position_up(final_room_pos)].add_down()
            elif (position_down(final_room_pos) in room_dict):
                final_room = room_dict[position_down(final_room_pos)].add_up()
            elif (position_left(final_room_pos) in room_dict):
                final_room = room_dict[position_left(final_room_pos)].add_right()
            elif (position_right(final_room_pos) in room_dict):
                final_room = room_dict[position_right(final_room_pos)].add_left()
            else:
                raise RuntimeError

            room_list.append(final_room)

        final_room.type = 'END'


        # create secret room
        free_positions = {} # dictionary holding neighbour count for each free position
        for room in room_list:
            for pos in room.get_free_neighbour_positions():
                if pos in (free_positions): 
                    free_positions[pos] += 1
                else:
                    # new entry
                    free_positions[pos] = 1
        # remove final room neighbours from candidates
        for pos in final_room.get_free_neighbour_positions():
            free_positions.pop(pos, None)

        # select random position from free positions having the maximum neighbour count
        secret_room_pos = random.choice(dict_inverse(free_positions)[max(free_positions.values())])

        # create and link secret room
        secret_room = Room(secret_room_pos, type='SECRET')
        FloorGenerator.__link_room(room_dict, secret_room)
        room_list.append(secret_room)

        # normalize room positions
        pos_x = []
        pos_y = []
        for room in room_list:
            pos_x.append(room.pos[0])
            pos_y.append(room.pos[1])
        min_x = min(pos_x)
        max_x = max(pos_x)
        min_y = min(pos_y)
        max_y = max(pos_y)
        floor_size = (max_x - min_x + 1, max_y - min_y + 1)
        for room in room_list:
            room.pos = (room.pos[0] - min_x, room.pos[1] - min_y)

        # select key room (room having key item to open final room door)
        key_room = random.choice([room for room in room_list if room.type == 'COMMON'])
        key_room.has_key = True
        
        # set door layout identifier
        for room in room_list:
            room.update_door_layout_code()

        return room_list, root_room, floor_size
