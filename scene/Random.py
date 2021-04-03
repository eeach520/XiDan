from Geometry.Arc import Arc
from Geometry.Point import Point
from Geometry.Triangle import Triangle
from Geometry.Vector import Vector
import random
import math


def generate_agent_in_circle(arc: Arc, n: int, r: float):
    """
    generate n point, every two points' distance is no more than r * 2
    :param arc:
    :param n:
    :param r:
    :return:
    """
    points = []
    while len(points) < n:
        p_r = random.uniform(0, arc.r - r)
        p_angle = random.uniform(0, math.pi * 2)
        p_x = arc.x + p_r * math.cos(p_angle)
        p_y = arc.y + p_r * math.sin(p_angle)
        is_valid = True
        for p in points:
            if math.sqrt((p.x - p_x) ** 2 + (p.y - p_y) ** 2) < r * 2:
                is_valid = False
                break
        if is_valid:
            points.append(Point(p_x, p_y))
    return points


def generate_agent_in_triangle(tri: Triangle, n: int, r: float):
    """
    generate n point randomly, every two points' distance is no less than r * 2
    :param tri:
    :param n:
    :param r:
    :return:
    """
    points = []
    mid = Point((tri.B.x + tri.C.x) / 2, (tri.B.y + tri.C.y) / 2)
    vb = Vector(tri.B.x - tri.A.x, tri.B.y - tri.A.y)
    vc = Vector(tri.C.x - tri.A.x, tri.C.y - tri.A.y)
    while len(points) < n:
        b = random.random()
        c = random.random()
        t = Vector.add(vb.mul(b), vc.mul(c))
        candi = Point(t.x + tri.A.x, t.y + tri.A.y)
        if not tri.is_inner_point(candi):
            candi = Point(2 * mid.x - candi.x, 2 * mid.y - candi.y)
        if tri.inner_dis(candi) < r:
            continue
        is_valid = True
        for p in points:
            if math.sqrt((p.x - candi.x) ** 2 + (p.y - candi.y) ** 2) < r * 2:
                is_valid = False
                break
        if is_valid:
            points.append(candi)
    return points
