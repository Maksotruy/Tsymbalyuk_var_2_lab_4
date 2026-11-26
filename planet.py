from game_object import GameObject


class Planet(GameObject):
    def in_atmosphere(self, x, y):
        return self.contains(x, y, 1)