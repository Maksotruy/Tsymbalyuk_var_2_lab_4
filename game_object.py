class GameObject:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def contains(self, x, y, border=0):
        return (
            self.x - border <= x <= self.x + self.size - 1 + border
            and
            self.y - border <= y <= self.y + self.size - 1 + border
        )

    def has_distance(self, other, distance):
        return (
            self.x + self.size + distance <= other.x
            or
            other.x + other.size + distance <= self.x
            or
            self.y + self.size + distance <= other.y
            or
            other.y + other.size + distance <= self.y
        )

    def intersection(self, x0, y0, x1, y1):
        low = 0
        high = 1

        axes = [
            (x0, x1 - x0, self.x),
            (y0, y1 - y0, self.y)
        ]

        for start, delta, origin in axes:
            a = origin - 1.5
            b = origin + self.size + 0.5

            if delta == 0:
                if not a <= start <= b:
                    return None

            else:
                t1, t2 = sorted((
                    (a - start) / delta,
                    (b - start) / delta
                ))

                low = max(low, t1)
                high = min(high, t2)

                if low > high:
                    return None

        return low