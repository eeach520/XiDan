from .Point import Point
from .Line import Line
from .Vector import Vector
from .LineSegment import LineSegment


class Triangle:
    def __init__(self, A: Point, B: Point, C: Point, index, is_entrance=False, eva_dir=None, near_index=-1,
                 min_eva_dis=9999999, bA=False, bB=False, bC=False):
        if eva_dir is None:
            eva_dir = []
        self.A, self.B, self.C = A, B, C
        self.center = Point((A.x + B.x + C.x) / 3, (A.y + B.y + C.y) / 3)
        self.index = index
        self.is_entrance = is_entrance
        self.eva_dir, self.near_index, self.min_eva_dis = eva_dir, near_index, min_eva_dis
        self.ls_A = LineSegment(B, C)
        self.ls_B = LineSegment(A, C)
        self.ls_C = LineSegment(B, A)
        self.bA, self.bB, self.bC = bA, bB, bC
        self.area = 0
        self.get_area()
        self.attacker_list = []
        self.pedestrian_list = []

    def is_inner_point(self, p: Point):
        li = [self.A, self.B, self.C]
        for i, pair in enumerate([[self.C, self.B], [self.A, self.C], [self.A, self.B]]):
            v1 = Vector(pair[0].x - li[i].x, pair[0].y - li[i].y)
            v2 = Vector(p.x - li[i].x, p.y - li[i].y)
            v3 = Vector(pair[1].x - li[i].x, pair[1].y - li[i].y)
            if Vector.cross_product(v1, v2) * Vector.cross_product(v2, v3) < 0:
                return False
        return True

    def inner_dis(self, p: Point):
        dis = float("inf")
        for ls in ([self.ls_A, self.bA], [self.ls_B, self.bB], [self.ls_C, self.bC]):
            if ls[1]:
                d = ls[0].line.distance(p)
                dis = min(dis, d)
        return dis

    def get_area(self):
        pB = Vector(self.B.x - self.A.x, self.B.y - self.A.y)
        pC = Vector(self.C.x - self.A.x, self.C.y - self.A.y)
        self.area = abs(Vector.cross_product(pB, pC)) / 2

    def common_lineSegment(self, other):
        pA = [self.A, self.B, self.C]
        pO = [other.A, other.B, other.C]
        c_p = [j for j in pA if j in pO]
        if len(c_p) != 2:
            raise ValueError("There is no common part or all common part in this two triangle.")
        return LineSegment(c_p[0], c_p[1])

    def get_attacker_list(self):
        return self.attacker_list

    def get_pedestrian_list(self):
        return self.pedestrian_list

    def remove_attacker(self, idx):
        self.attacker_list.remove(idx)

    def remove_pedestrian(self, idx):
        self.pedestrian_list.remove(idx)

    def append_attacker(self, idx):
        self.attacker_list.append(idx)

    def append_pedestrian(self, idx):
        self.pedestrian_list.append(idx)
