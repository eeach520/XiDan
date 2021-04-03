"""
set of Agent information
"""
import math
from Geometry.Point import Point
from Geometry.Vector import Vector
from matplotlib.patches import Circle, Arrow


class Agent:
    def __init__(self, center: Point, radius: float, v_max: float, tri_id=0):
        self.center = center
        # self.r = radius
        self.r = 400
        self.v_prf = None
        self.v_now = Vector(0, 0)
        self.v_max = v_max
        self.target = None
        self.tri_id = tri_id
        self.is_shown = True

    def plot(self, arrow_color):
        if self.v_now is not None and self.v_now.len > 1e-5:
            delta = math.sqrt(self.v_now.x ** 2 + self.v_now.y ** 2)
            dx, dy = self.r * 2 * self.v_now.x / delta, self.r * 2 * self.v_now.y / delta
            arw = Arrow(self.center.x, self.center.y, dx, dy, width=self.r / 5, color=arrow_color)
        else:
            arw = Arrow(self.center.x, self.center.y, self.center.x, self.center.y, color=arrow_color)
        # cir = Circle(xy=(self.center.x, self.center.y), radius=self.r, color=c_color)
        return arw

    def next_step(self, v):
        self.center = Point(self.center.x + v.x, self.center.y + v.y)
        self.v_now = v
