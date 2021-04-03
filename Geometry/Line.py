import math
from .Point import Point


class Line:
    """
    line in 2-D space
    """

    def __init__(self, a, b, c):
        """
        line formula in 2-D space: ax + by + c = 0
        :param a:
        :param b:
        :param c:
        """
        self.a, self.b, self.c = a, b, c

    def distance(self, p: Point):
        return abs(self.signed_distance(p))

    def signed_distance(self, p: Point) -> float:
        """
        signed distance is used in the RVO algorithm
        :param p:
        :return:
        """
        return (self.a * p.x + self.b * p.y + self.c) / math.sqrt(self.a ** 2 + self.b ** 2)

    def cross(self, line=None, a=None, b=None, c=None) -> Point:
        """
        accept two type parameter
        :param line:
        :param a:
        :param b:
        :param c:
        :return:
        """
        if line is not None:
            a, b, c = line.a, line.b, line.c
        if a is None or b is None or c is None:
            raise ValueError("parameter a,b,c is not defined.")
        D = a * self.b - b * self.a
        if abs(D) < 1e-6:
            raise ValueError('line({},{},{}) and line ({},{},{}) is parallel'.format(self.a, self.b, self.c, a, b, c))
        return Point((b * self.c - self.b * c) / D, (self.a * c - a * self.c) / D)

    def __str__(self):
        return "%.2fx + %.2fy + %.2f = 0" % (self.a, self.b, self.c)
