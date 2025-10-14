
import json
import pygame, os
from pygame.locals import *
from scene.dungeon.floor.tileset import Tileset
from utils.sprite_animation import *



class ResourceManager(object):
    resources = {}

    @classmethod
    def load_actor_database(cls):
        fullname = os.path.join(os.pardir, 'resources', 'database', 'actor_database.json')
        try:
            file = open(fullname)
            actor_database = json.load(file)
            file.close()
        except OSError:
            print ('Cannot load actor database')
            raise SystemExit
        return actor_database


    @classmethod
    def load_item_drop_databse(cls):
        fullname = os.path.join(os.pardir, 'resources', 'database', 'enemy_item_drops.json')
        try:
            file = open(fullname)
            item_drops_json = json.load(file)
            file.close()
            enemy_drops = {}
            for enemy_name, item_drops in item_drops_json["drop_weigths"].items():
                enemy_drops[enemy_name] = (list(item_drops.keys()), list(item_drops.values()))
        except OSError:
            print ('Cannot load item drop database')
            raise SystemExit
        return enemy_drops


    @classmethod
    def load_room_database(cls):
        fullname = os.path.join(os.pardir, 'resources', 'database', 'room_database.json')
        try:
            file = open(fullname)
            room_database = json.load(file)
            file.close()
        except OSError:
            print ('Cannot load room database')
            raise SystemExit
        return room_database


    @classmethod
    def load_floor_database(cls):
        fullname = os.path.join(os.pardir, 'resources', 'database', 'floor_database.json')
        try:
            file = open(fullname)
            floor_database = json.load(file)
            file.close()
        except OSError:
            print ('Cannot load room database')
            raise SystemExit
        return floor_database["floors"]


    @classmethod
    def load_image(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join(os.pardir, 'resources', 'images', name)
            try:
                image = pygame.image.load(fullname)
            except pygame.error:
                print ('Cannot load image:', fullname)
                raise SystemExit
            image = image.convert_alpha()
            cls.resources[name] = image
            return image


    @classmethod
    def load_sound(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join(os.pardir, 'resources', 'sounds', name)
            try:
                sound = pygame.mixer.Sound(fullname)
            except pygame.error:
                print ('Cannot load souns:', fullname)
                raise SystemExit
            cls.resources[name] = sound
            return sound


    @classmethod
    def load_music(cls, name, queue):
        fullname = os.path.join(os.pardir, 'resources', 'sounds', name)
        if queue:
            pygame.mixer.music.queue(fullname, loops=-1)
        else:
            pygame.mixer.music.load(fullname)
            


    @classmethod
    def load_animation(cls, name):
        if name in cls.resources:
            return SpriteAnimationFactory.get_animation_player(cls.resources[name])
        else:
            fullname = os.path.join(os.pardir, 'resources', 'animations', name)
            try:
                file = open(fullname)
                anim_json = json.load(file)
                file.close()

                anim_data = SpriteAnimationData(anim_json)
            except pygame.error:
                print ('Cannot load animation:', fullname)
                raise SystemExit
            cls.resources[name] = anim_data
            return SpriteAnimationFactory.get_animation_player(anim_data)


    @classmethod
    def load_room(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join(os.pardir, 'resources', 'rooms', name)
            try:
                file = open(fullname)
                room_data = json.load(file)
                file.close()
            except pygame.error:
                print ('Cannot load room:', fullname)
                raise SystemExit
            cls.resources[name] = room_data
            return room_data


    @classmethod
    def load_tileset(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join(os.pardir, 'resources', 'tilesets', name)
            try:
                file = open(fullname)
                tileset_json = json.load(file)
                tileset = Tileset(cls.load_image(tileset_json['image']),tileset_json['collisions'],tileset_json['size'])
                file.close()
            except pygame.error:
                print ('Cannot load room:', fullname)
                raise SystemExit
            cls.resources[name] = tileset
            return tileset
            