from game_object import GameObject


class Obstacle(GameObject):
    def in_danger_zone(self, x, y):
        return self.contains(x, y, 1)

    def at(self, turn):
        return self