
def dict_inverse(dct):
    inv_dct = {}
    for k, v in dct.items():
        inv_dct[v] = inv_dct.get(v, []) + [k]
    return inv_dct


def position_up(pos):
    return (pos[0],pos[1]-1)

def position_left(pos):
    return (pos[0]-1,pos[1])

def position_right(pos):
    return (pos[0]+1,pos[1])

def position_down(pos):
    return (pos[0],pos[1]+1)

def distance_to_origin(pos):
    return abs(pos[0]) + abs(pos[1])