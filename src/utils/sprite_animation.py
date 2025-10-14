
import pygame

class Keyframe:
    def __init__(self, time, value):
        self.time = time
        self.value = value


class SpriteAnimationData:

    def __init__(self, anim_json):
        sprite_size = anim_json["sprite_size"]

        # create rectangles
        self.rect_alts = {}
        for key, json_rect in anim_json["rects"].items():
            keyframes = []
            for time, value in json_rect.items():
                keyframes.append(Keyframe(int(time), pygame.Rect((value[1]*sprite_size[0], value[0]*sprite_size[1]), sprite_size)))
            self.rect_alts[key] = keyframes

        # animation frame count
        self.frame_count = anim_json["frame_count"]

        # current sprite alternative
        self.alt_key = anim_json["default_key"]
        self.default_key = anim_json["default_key"]

        # sprite count
        self.sprite_count = len(self.rect_alts[self.default_key])

        # add auxiliar last keyframe
        for alt_key, keyframes in self.rect_alts.items():
            keyframes.append(Keyframe(self.frame_count, None))

        self.loop = anim_json["loop"]


# abstract class
class SpriteAnimation:

    def __init__(self, animation_data):
        # animation data
        self.animation_data = animation_data
        # animation frame counter
        self.anim_counter = 0
        # current keyframe index
        self.current_keyframe_index = 0
        # set default animation
        self.current_animation = self.animation_data.rect_alts[animation_data.default_key]

    # reset animation
    def reset(self):
        self.anim_counter = 0
        self.current_keyframe_index = 0

    # change sprite alternative
    def set_alternative(self, alt_key):
        self.current_animation = self.animation_data.rect_alts[alt_key]

    # get current sprite rectangle
    def get_rect(self):
        return self.current_animation[self.current_keyframe_index].value

    # check animation playing ended
    def ended(self):
        return self.anim_counter > self.animation_data.frame_count

    def update(self, time):
        raise NotImplemented("'update' method must be implemented")



class SpriteAnimationLooped(SpriteAnimation):

    def __init__(self, animation_data):
        super().__init__(animation_data)

    def ended(self):
        return False

    def update(self,time):
        # loop frame counter and set corresponding keyframe
        self.anim_counter = (self.anim_counter + time) % self.animation_data.frame_count
        keyframe_count = len(self.current_animation)
        self.current_keyframe_index = next(i for i in range(keyframe_count) if self.current_animation[i].time > self.anim_counter) - 1
        

class SpriteAnimationNonLooped(SpriteAnimation):

    def __init__(self, animation_data):
        super().__init__(animation_data)

    def update(self, time):
        if (self.anim_counter > self.current_animation[self.current_keyframe_index + 1].time):
            self.current_keyframe_index = min(self.current_keyframe_index + 1, self.animation_data.sprite_count - 1)
        else:
            self.anim_counter += time


class SpriteAnimationFactory:

    @staticmethod
    def get_animation_player(animation_data):
        if animation_data.loop:
            return SpriteAnimationLooped(animation_data)
        else:
            return SpriteAnimationNonLooped(animation_data)
