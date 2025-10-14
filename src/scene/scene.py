
class Scene:

    def __init__(self, director):
        self.director = director

    # asbract method
    def update(self, *args):
        raise NotImplemented("'update' method must be implemented")

    # asbract method
    def events(self, *args):
        raise NotImplemented("'events' method must be implemented")

    # asbract method
    def draw(self, screen):
        raise NotImplemented("'draw' method must be implemented")
