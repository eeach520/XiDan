"""
Optimal Reciprocal Collision Avoidance Algorithm
"""

from Geometry.Vector import Vector
from Geometry.Point import Point
from Geometry.LineSegment import LineSegment
from Geometry.Line import Line
from Geometry.Arc import Arc
from Geometry.Ray import Ray
from .LP2D import LP2D_solution
from .LP3D import LP3D_solution
import math


def update(origin, VO: [], SO: [], t: int, v_max: float) -> Vector:
    """
    get the next optimal velocity.
    1) if ORCA half-planes has common part, then return V_old
    2) else return optimal velocity that 3-D linear programming solved
    :param v_max:
    :param t:
    :param origin: agent's info
    :param VO: velocity obstacle's info
    :param SO: static obstacle's info
    :return:
    """
    tmp = []
    for o in VO:
        if math.sqrt((origin.center.x - o.center.x) ** 2 + (
                origin.center.y - o.center.y) ** 2) <= t * 2 * origin.v_max + origin.r + o.r:
            tmp.append(o)
    SO_l = []
    for o in SO:
        if o.distance(origin.center) < origin.v_max * 2 + origin.r:
            SO_l.append(o)
    VO = tmp
    limit_2D = []
    for tar in VO:
        try:
            panel = get_ORCA_plane(origin, tar, t)
            if panel is not None:
                limit_2D.append(panel)
        except ValueError:
            print("collide happened")
    limit_SO = []
    for tar in SO_l:
        limit_SO.append(get_SO_plane(origin, tar, 2))
    # if flag and len(limit_2D) == 0:
    #     return origin.v_now
    f = origin.v_pref
    stat, res = LP2D_solution(limit_2D + limit_SO, f, v_max)
    if stat:
        for li in limit_2D:
            if res.x * li[0] + res.y * li[1] + li[2] > 1e-5:
                print("2D 结果不合法:", res.x * li[0] + res.y * li[1] + li[2])
        return Vector(res.x, res.y)
    print("2D no solution")
    limit_3D = []
    for limit in limit_2D:
        limit_3D.append([limit[0], limit[1], -1, limit[2]])
    for limit in limit_SO:
        limit_3D.append([limit[0], limit[1], 0, limit[2]])
    stat, res = LP3D_solution(limit_3D, [0, 0, -1], v_max / 1.414)
    if not stat:
        print("3D no solution")
        print(limit_3D)
        print(v_max)
        return Vector(0, 0)
    for lim in limit_3D:
        if lim[0] * res[0] + lim[1] * res[1] + lim[2] * res[2] + lim[3] > 1e-9:
            print("3D结果不合法")
    return Vector(res[0], res[1])


def get_ORCA_plane(origin, target, t: int):
    """
    get half-plane formula
    :param origin:
    :param target:
    :param t:
    :return:
    """
    VO_area = get_VO_area(origin, target, t)
    p = Point(origin.v_now.x - target.v_now.x, origin.v_now.y - target.v_now.y)
    # p = Point(- target.v_now.x, - target.v_now.y)
    n, u = closest_point_and_normal(VO_area, p)
    if target.v_now.x ** 2 + target.v_now.y ** 2 > 1e-2:
        u = u.mul(0.52)
    vt = Vector.add(origin.v_now, u)
    if is_target_out(VO_area, p):
        return [n.x, n.y, -vt.x * n.x - vt.y * n.y]
    return [-n.x, -n.y, vt.x * n.x + vt.y * n.y]


def is_target_out(area, p: Point):
    v1 = Vector(area[0].start.x, area[0].start.y)
    v2 = Vector(area[1].start.x, area[1].start.y)
    if Vector.cross_product(v1, p) * Vector.cross_product(p, v2) < 0:  # line outside
        return True
    if (p.x - area[2].x) ** 2 + (p.y - area[2].y) ** 2 > area[2].r ** 2:
        if p.x ** 2 + p.y ** 2 < area[2].x ** 2 + area[2].y ** 2:
            return True
    return False


def get_VO_area(origin, target, t: int):
    """
    a VO area means origin and target will collide in t seconds
    :param origin:
    :param target:
    :param t:
    :return:
    """
    velocity_center = Vector.sub(target.center, origin.center).div(t)
    r = (target.r + origin.r) / t
    v_circle = Arc(Point(velocity_center.x, velocity_center.y), r)
    points, lines = v_circle.tangent_line(Point(0, 0))
    v1 = Vector(points[0].x - velocity_center.x, points[0].y - velocity_center.y)
    v2 = Vector(points[1].x - velocity_center.x, points[1].y - velocity_center.y)
    if Vector.cross_product(v1, v2) > 0:
        arc = Arc.generate_arc_from_point(velocity_center, r, points[0], points[1])
    else:
        arc = Arc.generate_arc_from_point(velocity_center, r, points[1], points[0])
    if Vector.cross_product(points[0], points[1]) < 0:
        tmp = points[0]
        points[0] = points[1]
        points[1] = tmp
    ray1 = Ray(points[0], Vector(points[0].x, points[0].y))
    ray2 = Ray(points[1], Vector(points[1].x, points[1].y))
    return [ray1, ray2, arc]


def closest_point_and_normal(VO_area: [], p: Point):
    """
    get the closest point on VO with Va - Vb
    :param VO_area:
    :param p:
    :return:
    """
    normal, target_p, dis = None, None, float("inf")
    for border in VO_area:
        if isinstance(border, Ray):
            d, tp = border.distance(p)
            if d < dis:
                target_p, dis = tp, d
                normal = Vector(border.line.a, border.line.b).normalize()
        elif isinstance(border, Arc):
            d, tp = border.closest_point(p)
            if d < dis:
                target_p, dis = tp, d
                normal = Vector(tp.x - border.x, tp.y - border.y).normalize()
    u = Vector(target_p.x - p.x, target_p.y - p.y)
    if Vector.point_product(u, normal) < 0:
        normal = normal.mul(-1)
    return normal, u


def get_SO_plane(origin, target, t):
    SO_area = get_line_VO(origin, target, t)
    p = Point(0, 0)
    n, p = get_SO_closest_line(SO_area, p)
    a, b = n.x, n.y
    c = -a * p.x - b * p.y
    if c > 0:
        return [-a, -b, -c]
    return [a, b, c]


def get_SO_closest_line(SO_area, p):
    normal, target_p, dis = None, None, float("inf")
    for border in SO_area:
        if isinstance(border, Ray):
            d, tp = border.distance(p)
            if d < dis:
                target_p, dis = tp, d
                normal = Vector(border.line.a, border.line.b).normalize()
        elif isinstance(border, Arc):
            d, tp = border.closest_point(p)
            if d < dis:
                target_p, dis = tp, d
                normal = Vector(tp.x - border.x, tp.y - border.y).normalize()
        else:
            d, tp = border.closest_distance(p)
            if d < dis:
                target_p, dis = tp, d
                normal = Vector(border.line.a, border.line.b).normalize()
    u = Vector(target_p.x - p.x, target_p.y - p.y)
    if Vector.point_product(u, normal) < 0:
        normal = normal.mul(-1)
    return normal, target_p


def get_line_VO(origin, target, t):
    """
    VO  in t seconds
    :param origin:
    :param target: LineSegment,
    :param t:
    :return: five border of VO
    """
    start = Point((target.start.x - origin.center.x) / t, (target.start.y - origin.center.y) / t)  # 这里的点都是经过相互的位置然后除以时间变为速度
    end = Point((target.end.x - origin.center.x) / t, (target.end.y - origin.center.y) / t)
    lineSegment = LineSegment(start, end)
    v_r = origin.r / t
    a1, a2 = Arc(start, v_r), Arc(end, v_r)
    # b * start.x - a * start.y + c = 0
    # 利用垂线找到下面的切线，然后进行切割
    vp1, vp2 = a1.cross(Line(lineSegment.b, -lineSegment.a, lineSegment.a * start.y - lineSegment.b * start.x))
    l1 = Line(lineSegment.a, lineSegment.b, -lineSegment.a * vp1.x - lineSegment.b * vp1.y)
    l2 = Line(lineSegment.a, lineSegment.b, -lineSegment.a * vp2.x - lineSegment.b * vp2.y)
    r_line = get_closer_line(l1, l2)

    c_p1, c_p2 = a1.cross(r_line)[0], a2.cross(r_line)[0]
    t_line = LineSegment(c_p1, c_p2)
    p1, line1 = a1.limited_tangent_line(Point(0, 0))
    p2, line2 = a2.limited_tangent_line(Point(0, 0))
    pA = Vector(p1.x - start.x, p1.y - start.y)
    pB = Vector(p2.x - end.x, p2.y - end.y)
    pC = Vector(c_p1.x - start.x, c_p1.y - start.y)
    pD = Vector(c_p2.x - end.x, c_p2.y - end.y)
    if Vector.cross_product(pA, pC) > 0:
        arc1 = Arc.generate_arc_from_point(start, origin.r / t, p1, c_p1)
    else:
        arc1 = Arc.generate_arc_from_point(start, origin.r / t, c_p1, p1)
    if Vector.cross_product(pB, pD) > 0:
        arc2 = Arc.generate_arc_from_point(end, origin.r / t, p2, c_p2)
    else:
        arc2 = Arc.generate_arc_from_point(end, origin.r / t, c_p2, p2)
    ray1 = Ray(p1, Vector(p1.x, p1.y))
    ray2 = Ray(p2, Vector(p2.x, p2.y))
    return [ray1, arc1, t_line, arc2, ray2]


def SO_outer(area, p: Point) -> bool:
    if Vector.cross_product(area[0].start, p) * Vector.cross_product(p, area[4].start) < 0:
        return True
    if area[2].line.c * (area[2].line.a * p.x + area[2].line.b * p.y + area[2].line.c) > 0:
        return True
    if arc_outer(area[1], p) or arc_outer(area[3], p):
        return True
    return False


def arc_outer(arc: Arc, p: Point):
    pA = Vector(arc.start_p.x - arc.x, arc.start_p.y - arc.y)
    pB = Vector(p.x - arc.x, p.y - arc.y)
    pC = Vector(arc.end_p.x - arc.x, arc.end_p.y - arc.y)
    if Vector.cross_product(pA, pB) * Vector.cross_product(pB, pC) > 0:
        if (p.x - arc.x) ** 2 + (p.y - arc.y) ** 2 > arc.r ** 2:
            return True
    return False


def get_closer_line(line1, line2):
    """
    get the line closer to (0, 0)
    :param line1:
    :param line2:
    :return:
    """
    if abs(line1.c) > abs(line2.c):
        return line2
    else:
        return line1
