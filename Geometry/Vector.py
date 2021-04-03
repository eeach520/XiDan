import math


class Vector:
    """
    vector in 2-D space
    """

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.len = math.sqrt(x ** 2 + y ** 2)

    def normalize(self):
        if abs(self.len) < 1e-9:
            raise ValueError("vector length is zero")
        return Vector(self.x / self.len, self.y / self.len)

    def angle(self):
        ag = math.acos(self.x / self.len) / math.pi * 180
        if self.y < 0:
            ag += 180
        return ag

    def mul(self, t):
        return Vector(self.x * t, self.y * t)

    def div(self, t):
        return Vector(self.x / t, self.y / t)

    def __str__(self):
        return "[{},{}]".format(self.x, self.y)

    @staticmethod
    def add(vec1, vec2):
        return Vector(vec1.x + vec2.x, vec1.y + vec2.y)

    @staticmethod
    def sub(vec1, vec2):
        return Vector(vec1.x - vec2.x, vec1.y - vec2.y)

    @staticmethod
    def cross_product(vec1, vec2):
        return vec1.x * vec2.y - vec1.y * vec2.x

    @staticmethod
    def point_product(vec1, vec2):
        return vec1.x * vec2.x + vec1.y * vec2.y

    @staticmethod
    def cross_angle(vec1, vec2):
        """
        use angle(360) not radian(2*pi)
        :param vec1:
        :param vec2:
        :return:
        """
        if vec1.len < 1e-9 or vec2.len < 1e-9:
            return 0
        return math.acos(Vector.point_product(vec1, vec2) / vec1.len / vec2.len) / math.pi * 180
