"""
describe a ray
"""

import math
from .Point import Point
from .Vector import Vector
from .Line import Line


class Ray:
    def __init__(self, start: Point, v: Vector):
        self.start, self.v = start, v
        c = -(v.y * start.x - v.x * start.y)
        self.line = Line(v.y, -v.x, c)

    def is_inner(self, p: Point):
        if abs(self.line.a * p.x + self.line.b * p.y + self.line.c) > 1e-9:
            return False
        v = Vector(p.x - self.start.x, p.y - self.start.y)
        return Vector.point_product(v, self.v) >= 0

    def distance(self, p: Point):
        real_distance = self.line.distance(p)
        vertical_point = self.line.cross(a=self.line.b, b=-self.line.a, c=self.line.a * p.y - self.line.b * p.x)
        if self.is_inner(vertical_point):
            return real_distance, vertical_point
        return math.sqrt((p.x - self.start.x) ** 2 + (p.y - self.start.y) ** 2), self.start
