import math
from .Point import Point
from .Line import Line
from .Vector import Vector


class LineSegment:
    """
    using line formula ax + by + c = 0 with two points
    """

    def __init__(self, start: Point, end: Point):
        self.start, self.end = start, end
        self.a, self.b, self.c = end.y - start.y, start.x - end.x, end.x * start.y - start.x * end.y
        self.line = Line(self.a, self.b, self.c)

    def distance(self, p: Point):
        """
        return min distance when vertical point is not in segment
        :param p:
        :return:
        """
        real_distance = self.line.distance(p)
        if real_distance < 1e-9:
            return 0

        vertical_point = self.line.cross(a=self.b, b=-self.a, c=self.a * p.y - self.b * p.x)
        pA = Vector(self.start.x - p.x, self.start.y - p.y)
        pB = Vector(self.end.x - p.x, self.end.y - p.y)
        pT = Vector(vertical_point.x - p.x, vertical_point.y - p.y)
        if Vector.cross_product(pA, pT) * Vector.cross_product(pT, pB) > 0:
            return real_distance

        dS = math.sqrt((self.start.x - p.x) ** 2 + (self.start.y - p.y) ** 2)
        dE = math.sqrt((self.end.x - p.x) ** 2 + (self.end.y - p.y) ** 2)
        return min(dS, dE)

    def closest_distance(self, p: Point):
        real_distance = self.line.distance(p)
        vertical_point = self.line.cross(a=self.b, b=-self.a, c=self.a * p.y - self.b * p.x)
        if abs(self.distance(p) - real_distance) < 1e-9:
            return real_distance, vertical_point
        dS = math.sqrt((self.start.x - p.x) ** 2 + (self.start.y - p.y) ** 2)
        dE = math.sqrt((self.end.x - p.x) ** 2 + (self.end.y - p.y) ** 2)
        if dS > dE:
            return dE, self.end
        return dS, self.start

    def is_inner(self, p: Point):
        delta = self.a * p.x + self.b * p.y + self.c
        return abs(delta) < 1e-9 and self.start.x <= p.x <= self.end.x

    def cross(self, a, b, c) -> bool:
        real_cross_point = self.line.cross(a=a, b=b, c=c)
        return self.is_inner(real_cross_point)

    def evade_vector(self, p: Point):
        _, des = self.closest_distance(p)
        return Vector(des.x - p.x, des.y - p.y)

    def segment_cross(self, line) -> bool:
        """
        segment has common part
        :param line:
        :return:
        """
        real_cross_point = self.line.cross(a=line.a, b=line.b, c=line.c)
        return self.is_inner(real_cross_point) and line.is_inner(real_cross_point)
