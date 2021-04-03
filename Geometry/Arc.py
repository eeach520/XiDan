import math
from .Point import Point
from .Line import Line
from .Vector import Vector
from .LineSegment import LineSegment


class Arc:
    def __init__(self, center: Point, radius, start_angle=0, end_angle=360, start_p=None, end_p=None):
        self.x, self.y = center.x, center.y
        self.r = radius
        self.sA, self.eA = start_angle, end_angle
        self.start_p, self.end_p = start_p, end_p

    def cross(self, line: Line):
        if line.distance(Point(self.x, self.y))- self.r > 1e-6:
            raise ValueError(
                "line({},{},{}) and arc({},{},{}) hasn't common part".format(line.a, line.b, line.c, self.x, self.y,
                                                                             self.r))
        if abs(line.b) < 1e-6:
            pX = -line.c / line.a
            pY1 = self.y + math.sqrt(abs(self.r ** 2 - (pX - self.x) ** 2))
            pY2 = self.y - math.sqrt(abs(self.r ** 2 - (pX - self.x) ** 2))
            return [Point(pX, pY1), Point(pX, pY2)]
        e, f = line.a / line.b, line.c / line.b + self.y
        a, b, c = 1 + e ** 2, 2 * e * f - 2 * self.x, f ** 2 + self.x ** 2 - self.r ** 2
        delta = math.sqrt(abs(b ** 2 - 4 * a * c))
        pX1, pX2 = (-b + delta) / 2 / a, (-b - delta) / 2 / a
        return [Point(pX1, -(line.c + line.a * pX1) / line.b), Point(pX2, -(line.c + line.a * pX2) / line.b)]

    def is_inner(self, p: Point):
        pT = Vector(p.x - self.x, p.y - self.y)
        angle = pT.angle()
        return self.sA <= angle <= self.eA or self.sA <= angle + 360 <= self.eA

    def tangent_line(self, p: Point):
        if (p.x - self.x) ** 2 + (p.y - self.y) ** 2 <= self.r ** 2:
            raise ValueError("point {} is in the circle, it should in outside".format(p))
        """
        formula: Ax = By + C
        """
        A = self.x - p.x
        B = p.y - self.y
        C = self.x ** 2 + self.y ** 2 - self.x * p.x - self.y * p.y - self.r ** 2
        if abs(A) < 1e-9:
            y = -C / B
            delta = math.sqrt(self.r ** 2 - (y - self.y) ** 2)
            x1, x2 = self.x + delta, self.x - delta
            p1, p2 = Point(x1, y), Point(x2, y)
        else:
            D, E = B / A, C / A
            a = D ** 2 + 1
            b = 2 * (E - self.x) * D - 2 * self.y
            c = (E - self.x) ** 2 + self.y ** 2 - self.r ** 2
            delta = b ** 2 - 4 * a * c
            if delta < 0:
                raise ValueError("no solution!")
            delta = math.sqrt(delta)
            y1, y2 = -(b + delta) / 2 / a, -(b - delta) / 2 / a
            x1, x2 = D * y1 + E, D * y2 + E
            p1, p2 = Point(x1, y1), Point(x2, y2)
        return [p1, p2], [LineSegment(p1, p).line, LineSegment(p2, p).line]

    def limited_tangent_line(self, p: Point):
        if (p.x - self.x) ** 2 + (p.y - self.y) ** 2 <= self.r ** 2:
            raise ValueError("point {} is in the circle, it should in outside".format(p))
        """
        formula: Ax = By + C
        """
        A = self.x - p.x
        B = p.y - self.y
        C = self.x ** 2 + self.y ** 2 - self.x * p.x - self.y * p.y - self.r ** 2
        if abs(A) < 1e-9:
            y = -C / B
            delta = math.sqrt(self.r ** 2 - (y - self.y) ** 2)
            x1, x2 = self.x + delta, self.x - delta
            p1, p2 = Point(x1, y), Point(x2, y)
        else:
            D, E = B / A, C / A
            a = D ** 2 + 1
            b = 2 * (E - self.x) * D - 2 * self.y
            c = (E - self.x) ** 2 + self.y ** 2 - self.r ** 2
            delta = b ** 2 - 4 * a * c
            if delta < 0:
                raise ValueError("no solution!")
            delta = math.sqrt(delta)
            y1, y2 = -(b + delta) / 2 / a, -(b - delta) / 2 / a
            x1, x2 = D * y1 + E, D * y2 + E
            p1, p2 = Point(x1, y1), Point(x2, y2)
        if self.is_inner(p1):
            return p1, LineSegment(p1, p).line
        else:
            return p2, LineSegment(p2, p).line

    def closest_point(self, p: Point):
        if abs(p.x - self.x) + abs(self.y - p.y) < 1e-6:
            li = LineSegment(Point(0, 0), p).line
        else:
            li = LineSegment(Point(self.x, self.y), p).line
        cross_point = self.cross(li)  # 这里的代码是求一个交点，求出圆内一点到垂线
        candi = []
        for cp in cross_point:
            if self.is_inner(cp):
                candi.append(cp)
        if len(candi) == 0:
            candi.append(self.start_p)
            candi.append(self.end_p)
        dis, tp = float("inf"), None
        for cp in candi:
            d = math.sqrt((cp.x - p.x) ** 2 + (cp.y - p.y) ** 2)
            if d < dis:
                dis, tp = d, cp
        return dis, tp

    @staticmethod
    def generate_arc_from_point(center: Point, radius: float, start: Point, end: Point):
        pT1, pT2 = Vector(start.x - center.x, start.y - center.y), Vector(end.x - center.x, end.y - center.y)
        ag1, ag2 = pT1.angle(), pT2.angle()
        if ag2 < ag1:
            ag2 += 360
        return Arc(center, radius, ag1, ag2, start, end)
