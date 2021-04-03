"""
set of Agent information
"""
import math
from Geometry.Point import Point
from Geometry.Vector import Vector
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


class Agent:
    def __init__(self, center: Point, t_point: Point, radius: float, v_max: float):
        self.center = center
        self.r = radius
        self.v_pref = Vector(t_point.x - center.x, t_point.y - center.y).normalize().mul(v_max)
        self.v_now = self.v_pref
        self.v_max = v_max
        self.target = t_point

    def plot(self):
        delta = math.sqrt(self.v_now.x ** 2 + self.v_now.y ** 2)
        dx, dy = self.r * self.v_now.x / delta * 2, self.r * self.v_now.y / delta * 2
        return [self.center.x, self.center.y, dx, dy]

    def next_step(self, v):
        if math.sqrt((self.target.x - self.center.x) ** 2 + (self.target.y - self.center.y) ** 2) < 4:
            self.v_pref = Vector(0, 0)
            self.v_now = Vector(0, 0)
            return
        if abs(v.x) + abs(v.y) < 1e-9:
            try:
                self.v_pref = Vector(self.target.x - self.center.x, self.target.y - self.center.y).normalize().mul(
                    self.v_max)
            except ValueError:
                self.v_pref = Vector(0, 0)
            self.v_now = self.v_pref
        else:
            self.center = Point(self.center.x + v.x, self.center.y + v.y)
            try:
                self.v_pref = Vector(self.target.x - self.center.x, self.target.y - self.center.y).normalize().mul(
                    self.v_max)
            except ValueError:
                self.v_pref = Vector(0, 0)
            self.v_now = v
