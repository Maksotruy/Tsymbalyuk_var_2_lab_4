import math

from obstacle import Obstacle
from config import MOVING_SYMBOLS


class MovingObstacle(Obstacle):

    def __init__(
        self,
        x,
        y,
        size,
        dx,
        dy,
        speed,
        travel
    ):

        super().__init__(x, y, size)

        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.travel = travel

        self.period = (
            2 * travel
            // math.gcd(speed, 2 * travel)
        )

    def offset(self, turn):

        position = (
            turn * self.speed
        ) % (2 * self.travel)

        if position <= self.travel:

            return position

        return 2 * self.travel - position

    def at(self, turn):

        offset = self.offset(turn)

        return Obstacle(
            self.x + self.dx * offset,
            self.y + self.dy * offset,
            self.size
        )

    def arrow(self, turn):

        position = (
            turn * self.speed
        ) % (2 * self.travel)

        direction = (
            1 if position < self.travel else -1
        )

        return MOVING_SYMBOLS[
            (
                self.dx * direction,
                self.dy * direction
            )
        ]

    def all_positions(self):

        return [
            Obstacle(
                self.x + self.dx * offset,
                self.y + self.dy * offset,
                self.size
            )

            for offset in range(
                self.travel + 1
            )
        ]

    def hits_during_move(self, x, y, turn):

        for step in range(self.speed):

            phase = (
                turn * self.speed + step
            ) % (2 * self.travel)

            next_phase = (
                phase + 1
            ) % (2 * self.travel)

            a = min(
                phase,
                2 * self.travel - phase
            )

            b = min(
                next_phase,
                2 * self.travel - next_phase
            )

            start_x = self.x + self.dx * a
            start_y = self.y + self.dy * a

            end_x = self.x + self.dx * b
            end_y = self.y + self.dy * b

            obstacle = Obstacle(
                start_x,
                start_y,
                self.size
            )

            relative_x = x - (end_x - start_x)
            relative_y = y - (end_y - start_y)

            if obstacle.intersection(
                x,
                y,
                relative_x,
                relative_y
            ) is not None:

                return True

        return False