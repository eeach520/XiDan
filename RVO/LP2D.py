"""
solution to linear programming in 2-D space
"""
from Geometry.Vector import Vector
from Geometry.Line import Line
from Geometry.Arc import Arc
from Geometry.Point import Point
from random import shuffle


def LP2D_solution(pl: [], f: Vector, M: float):
    """
    dealing with vertical line
    :param pl:
    :param f:
    :param M:
    :return:
    """
    for p in pl:
        if abs(p[1]) < 1e-9:
            p[1] = p[0] / 1000
    if abs(f.x) < 1e-9 and abs(f.y) < 1e-9:
        f = Vector(1e-3, 1e-3)
    return randomized_bounded_LP2D(pl, f, M)


def randomized_bounded_LP2D(pl: [], f: Vector, M: float):
    """
    compute linear programming in a circle with radius M
    :param pl:
    :param f:
    :param M:
    :return:
    """
    shuffle(pl)
    border = []
    arc, v = init(f, M)
    n_inf, p_inf = -float("inf"), float("inf")
    for param in pl:
        if param[0] * v.x + param[1] * v.y + param[2] <= 1e-5:
            border.append(Line(param[0], param[1], param[2]))
            continue
        li = Line(param[0], param[1], param[2])
        pos = Vector(param[1], -param[0]).normalize().div(1e5)
        if pos.x < 0:
            pos = pos.mul(-1)
        left, right = Vector(n_inf, 0), Vector(p_inf, 0)
        try:
            points = arc.cross(li)
            for p in points:
                test_point = Vector(pos.x + p.x, pos.y + p.y)
                if test_point.x ** 2 + test_point.y ** 2 - M ** 2 <= 0:
                    if left.x < p.x:
                        left = p
                else:
                    if right.x > p.x:
                        right = p
        except ValueError:
            return False, None

        for edge in border:
            try:
                cross_point = li.cross(line=edge)
                test_point = Vector(pos.x + cross_point.x, pos.y + cross_point.y)
                if test_point.x * edge.a + test_point.y * edge.b + edge.c <= 0:
                    if left.x < cross_point.x:
                        left = cross_point
                else:
                    if right.x > cross_point.x:
                        right = cross_point
            except ValueError:
                continue
        if right.x < left.x or left.x == n_inf or right.x == p_inf:
            return False, None
        if Vector.point_product(f, left) > Vector.point_product(f, right):
            v = left
        else:
            v = right
        border.append(li)
    return True, v


def init(f: Vector, M: float):
    """
    choose optimal point in circle space
    :param f:
    :param M:
    :return:
    """
    arc = Arc(Point(0, 0), M)
    normal = Line(f.y, -f.x, 0)
    points = arc.cross(normal)
    v, target = None, -float("inf")
    for p in points:
        if Vector.point_product(p, f) > target:
            v, target = p, Vector.point_product(p, f)
    return arc, v
