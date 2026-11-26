from game_object import GameObject


class Spaceship(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 1)

        self.alive = True

    def move(self, x, y):
        self.x = x
        self.y = y

    def crash(self):
        self.alive = False