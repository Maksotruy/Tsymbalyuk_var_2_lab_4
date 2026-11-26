import random
import math

from collections import deque

from config import (
    LEVELS,
    DIFFICULTIES,
    MIN_DISTANCE,
    MAX_FIELD_SIZE,
    MAX_GENERATION_ATTEMPTS,
    DYNAMIC_SETTINGS
)

from planet import Planet
from obstacle import Obstacle
from moving_obstacle import MovingObstacle
from spaceship import Spaceship


class Game:

    def __init__(
        self,
        mode,
        difficulty,
        width,
        height
    ):

        self.mode = mode
        self.difficulty = difficulty

        self.width = width
        self.height = height

        index = list(
            DIFFICULTIES.values()
        ).index(difficulty)

        (
            self.count,
            self.moving,
            self.sizes,
            self.max_move,
            self.required,
            self.min_field
        ) = LEVELS[mode][index]

        self.settings = DYNAMIC_SETTINGS[
            difficulty
        ]

        if not all(
            self.min_field <= n <= MAX_FIELD_SIZE
            for n in (width, height)
        ):

            raise ValueError(
                "Недопустимий розмір поля!"
            )

        self.__steps = 0

        self.minimum_steps = None

        self.obstacles = []

        self.positions = {}

        self.period = 1

        self.offsets = []

        self.path_cache = {}

        self.prepare_offsets()

        self.generate()

    @property
    def steps(self):

        return self.__steps

    def prepare_offsets(self):

        self.offsets = []

        if self.max_move is None:

            self.offsets = [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1)
            ]

            return

        for dx in range(
            -self.max_move,
            self.max_move + 1
        ):

            for dy in range(
                -self.max_move,
                self.max_move + 1
            ):

                if (
                    0 < dx * dx + dy * dy
                    <= self.max_move ** 2
                ):

                    self.offsets.append(
                        (dx, dy)
                    )

        self.offsets.sort(
            key=lambda p: (
                p[0] ** 2 + p[1] ** 2
            ),
            reverse=True
        )

    def bounds(self, x, y):

        return (
            0 <= x < self.width
            and
            0 <= y < self.height
        )

    def object_bounds(self, obj):

        return (
            1 <= obj.x
            <= self.width - obj.size - 1
            and
            1 <= obj.y
            <= self.height - obj.size - 1
        )

    def random_object(self, cls, size):

        return cls(
            random.randint(
                1,
                self.width - size - 1
            ),

            random.randint(
                1,
                self.height - size - 1
            ),

            size
        )

    def planet_center(self):

        return (
            self.planet.x
            + (self.planet.size - 1) / 2,

            self.planet.y
            + (self.planet.size - 1) / 2
        )

    def distance_to_planet(self, x, y):

        dx = max(
            self.planet.x - 1.5 - x,
            0,
            x - self.planet.x
            - self.planet.size - 0.5
        )

        dy = max(
            self.planet.y - 1.5 - y,
            0,
            y - self.planet.y
            - self.planet.size - 0.5
        )

        return math.hypot(dx, dy)

    def generate_planet(self):

        size = random.randint(4, 5)

        self.planet = self.random_object(
            Planet,
            size
        )

    def generate_ship(self):

        candidates = []

        minimum_distance = (
            min(self.width, self.height)
            * 0.45
        )

        if self.max_move is not None:

            minimum_distance = max(
                minimum_distance,
                (self.required - 1)
                * self.max_move + 1
            )

        for x in range(self.width):

            for y in range(self.height):

                if self.planet.in_atmosphere(
                    x,
                    y
                ):

                    continue

                distance = self.distance_to_planet(
                    x,
                    y
                )

                if distance >= minimum_distance:

                    candidates.append(
                        (x, y)
                    )

        if not candidates:

            return False

        x, y = random.choice(candidates)

        self.ship = Spaceship(x, y)

        return True

    def route_distance(self, x, y):

        ax = self.ship.x
        ay = self.ship.y

        bx, by = self.planet_center()

        dx = bx - ax
        dy = by - ay

        length = dx * dx + dy * dy

        if length == 0:

            return math.hypot(
                x - ax,
                y - ay
            )

        t = (
            (x - ax) * dx
            + (y - ay) * dy
        ) / length

        t = max(
            0,
            min(1, t)
        )

        px = ax + t * dx
        py = ay + t * dy

        return math.hypot(
            x - px,
            y - py
        )

    def route_position(self, size):

        ax = self.ship.x
        ay = self.ship.y

        bx, by = self.planet_center()

        t = random.uniform(
            0.15,
            0.85
        )

        dx = bx - ax
        dy = by - ay

        length = math.hypot(dx, dy)

        if length == 0:

            length = 1

        px = ax + t * dx
        py = ay + t * dy

        corridor = max(
            4,
            min(
                self.width,
                self.height
            ) * 0.22
        )

        offset = random.uniform(
            -corridor,
            corridor
        )

        px += -dy / length * offset
        py += dx / length * offset

        x = round(
            px - (size - 1) / 2
        )

        y = round(
            py - (size - 1) / 2
        )

        x = max(
            1,
            min(
                self.width - size - 1,
                x
            )
        )

        y = max(
            1,
            min(
                self.height - size - 1,
                y
            )
        )

        return x, y

    def get_directions(self):

        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]

        if self.settings["diagonal"]:

            directions.extend([
                (1, 1),
                (-1, -1),
                (1, -1),
                (-1, 1)
            ])

        return directions

    def create_obstacle(
        self,
        moving,
        near_route
    ):

        size = random.randint(
            *self.sizes
        )

        if near_route:

            x, y = self.route_position(
                size
            )

        else:

            x = random.randint(
                1,
                self.width - size - 1
            )

            y = random.randint(
                1,
                self.height - size - 1
            )

        if not moving:

            return Obstacle(
                x,
                y,
                size
            )

        dx, dy = random.choice(
            self.get_directions()
        )

        speed = random.randint(
            *self.settings["speed"]
        )

        travel = random.randint(
            *self.settings["travel"]
        )

        return MovingObstacle(
            x,
            y,
            size,
            dx,
            dy,
            speed,
            travel
        )

    def get_positions(self, obj):

        if isinstance(
            obj,
            MovingObstacle
        ):

            return obj.all_positions()

        return [obj]

    def valid_obstacle(
        self,
        obj,
        reserved,
        near_route
    ):

        positions = self.get_positions(
            obj
        )

        for position in positions:

            if not self.object_bounds(
                position
            ):

                return False

            if position.in_danger_zone(
                self.ship.x,
                self.ship.y
            ):

                return False

            if not position.has_distance(
                self.planet,
                MIN_DISTANCE
            ):

                return False

            for other in reserved:

                if not position.has_distance(
                    other,
                    MIN_DISTANCE
                ):

                    return False

        if near_route:

            corridor = max(
                4,
                min(
                    self.width,
                    self.height
                ) * 0.22
            )

            distance = min(
                self.route_distance(
                    p.x + (p.size - 1) / 2,
                    p.y + (p.size - 1) / 2
                )

                for p in positions
            )

            if distance > corridor:

                return False

        return True

    def generate_obstacles(self, attempt=0):

        self.obstacles = []

        reserved = []

        route_count = 0

        if self.mode == "Розширений":

            route_count = math.ceil(
                self.count
                * self.settings["route_ratio"]
            )

            route_count = max(
                self.moving,
                route_count - attempt // 10
            )

        for i in range(self.count):

            moving = i < self.moving

            near_route = i < route_count

            found = False

            for trial in range(1200):

                prefer_route = (
                    near_route
                    and trial < 400
                )

                obj = self.create_obstacle(
                    moving,
                    prefer_route
                )

                if not self.valid_obstacle(
                    obj,
                    reserved,
                    prefer_route
                ):

                    continue

                self.obstacles.append(
                    obj
                )

                reserved.extend(
                    self.get_positions(obj)
                )

                found = True

                break

            if not found:

                return False

        return True

    def prepare_positions(self):

        self.period = 1

        for obj in self.obstacles:

            if isinstance(
                obj,
                MovingObstacle
            ):

                self.period = math.lcm(
                    self.period,
                    obj.period
                )

        self.positions = {}

        self.path_cache = {}

    def obstacles_at(self, turn):

        phase = turn % self.period

        if phase not in self.positions:

            self.positions[phase] = [
                obj.at(phase)
                if isinstance(
                    obj,
                    MovingObstacle
                )
                else obj

                for obj in self.obstacles
            ]

        return self.positions[phase]

    def analyze(
        self,
        x,
        y,
        nx,
        ny,
        turn
    ):

        phase = turn % self.period

        planet_time = self.planet.intersection(
            x,
            y,
            nx,
            ny
        )

        hit_time = None

        for obj in self.obstacles_at(
            phase
        ):

            time = obj.intersection(
                x,
                y,
                nx,
                ny
            )

            if time is not None:

                if (
                    hit_time is None
                    or time < hit_time
                ):

                    hit_time = time

        if hit_time is not None:

            if (
                planet_time is None
                or hit_time <= planet_time
            ):

                return "lose", hit_time

        if planet_time is not None:

            return "win", planet_time

        for obj in self.obstacles:

            if isinstance(
                obj,
                MovingObstacle
            ):

                if obj.hits_during_move(
                    nx,
                    ny,
                    phase
                ):

                    return "lose", 1

        return "continue", 1

    def solve(self, x, y):

        queue = deque([
            (x, y, 0, 0)
        ])

        visited = {
            (x, y, 0)
        }

        while queue:

            x, y, phase, steps = (
                queue.popleft()
            )

            for dx, dy in self.offsets:

                nx = x + dx
                ny = y + dy

                if not self.bounds(
                    nx,
                    ny
                ):

                    continue

                next_phase = (
                    phase + 1
                ) % self.period

                state = (
                    nx,
                    ny,
                    next_phase
                )

                result, time = self.analyze(
                    x,
                    y,
                    nx,
                    ny,
                    phase
                )

                if result == "win":

                    return steps + 1

                if result == "lose":

                    continue

                if state in visited:

                    continue

                visited.add(
                    state
                )

                queue.append((
                    nx,
                    ny,
                    next_phase,
                    steps + 1
                ))

        return None

    def generate(self):

        self.minimum_steps = None

        for attempt in range(
            MAX_GENERATION_ATTEMPTS
        ):

            self.generate_planet()

            if not self.generate_ship():

                continue

            if not self.generate_obstacles(
                attempt
            ):

                continue

            self.prepare_positions()

            minimum = self.solve(
                self.ship.x,
                self.ship.y
            )

            if minimum is None:

                continue

            if minimum < self.required:

                continue

            if self.max_move is not None:

                self.minimum_steps = minimum

            else:

                self.minimum_steps = None

            return

        raise RuntimeError(
            "Не вдалося створити прохідне поле. "
            "Повторіть спробу або збільште поле."
        )

    def move(self, x, y):

        if not self.bounds(x, y):

            raise ValueError(
                "Координати за межами поля!"
            )

        dx = x - self.ship.x
        dy = y - self.ship.y

        if dx == 0 and dy == 0:

            raise ValueError(
                "Корабель вже у цій точці!"
            )

        if self.max_move is not None:

            if (
                dx * dx + dy * dy
                > self.max_move ** 2
            ):

                raise ValueError(
                    "Перевищено дальність польоту!"
                )

        result, time = self.analyze(
            self.ship.x,
            self.ship.y,
            x,
            y,
            self.steps
        )

        new_x = round(
            self.ship.x + dx * time
        )

        new_y = round(
            self.ship.y + dy * time
        )

        new_x = max(
            0,
            min(
                self.width - 1,
                new_x
            )
        )

        new_y = max(
            0,
            min(
                self.height - 1,
                new_y
            )
        )

        self.ship.move(
            new_x,
            new_y
        )

        self.__steps += 1

        if result == "lose":

            self.ship.crash()

        return result