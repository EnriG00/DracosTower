
from actors.actor import Actor


class KillEnemiesObserver(Actor):

    def __init__(self, dungeon, enemies):
        Actor.__init__(self)

        self.dungeon = dungeon
        self.enemies = enemies

    def update(self, time):
        # check enemy group is empty
        if not self.enemies:
            self.dungeon.complete_room()
            self.kill()

    def player_react(self, player):
        return

    def map_collide(self, map_collisions, time):
        return

    def player_collide(self, player):
        return