


import random
from actors.actor import DamageActor, LifeActor
from utils.enemy_drop_generator import EnemyDropGenerator
from actors.enemy_kill_effect import EnemyKillEffect


class Enemy(DamageActor, LifeActor):

    def __init__(self, pos, dir, speed, life):
        LifeActor.__init__(self, pos, dir, speed, life)


    def add_to_groups(self, room_context):
        super(Enemy, self).add_to_groups(room_context)
        room_context.enemies.add(self)

    def player_collide(self, player):
        self.damage(player)

    def die(self):
        # create kill effect
        self.dungeon.add_actor(EnemyKillEffect(self.rect.center))
        self.kill()
        # create item drop randomly
        if self.DROP_CHANCE > random.uniform(0,1):
            self.dungeon.add_actor(EnemyDropGenerator.generate_item(self, self.rect.topleft))