from DXF.DXFReader import DXFReader
from scene.Random import generate_agent_in_triangle, generate_agent_in_circle
from Geometry.Arc import Arc
from Geometry.Point import Point
from Geometry.LineSegment import LineSegment
from Geometry.Vector import Vector
from .Agent import Agent
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
from matplotlib.animation import FuncAnimation
import math
import logging
import random


def plot_figure(n):
    print("godddd")


class Evacuation:
    def __init__(self, attacker, pedestrian, shown=True):
        self.attack_pos = []
        self.reader = DXFReader()
        self.attack, self.pedestrian = attacker, pedestrian
        self.attack_tri = []
        self.pedestrian_pos = []
        self.tris = self.reader.get_tris()
        self.valid_area = 0
        self.attack_agents = []
        self.pedestrian_agents = []
        self.point_map = self.reader.get_point_map()
        self.ani, self.fig, self.ax = None, None, None
        self.r_view = 8000
        self.r_panic = 1000

    def init_attacker(self):
        attacker_area = self.reader.get_attacker()
        for area in attacker_area:
            arc = Arc(Point(area["center"].x, area["center"].y), area["radius"])
            self.attack_pos += generate_agent_in_circle(arc, self.attack["number"] / len(attacker_area),
                                                        self.attack["radius"])
        for p in self.attack_pos:
            self.attack_agents.append(Agent(p, self.attack["radius"], self.attack["v_max"]))
        for i, ag in enumerate(self.attack_agents):
            for tri in self.tris:
                if tri.is_inner_point(ag.center):
                    tri.append_attacker(i)
                    ag.tri_id = tri.index
                    logging.debug("{} attacker find tri".format(i))
                    break

    def init_pedestrian(self):
        for i, p in enumerate(self.attack_pos):
            for tri in self.tris:
                if tri.is_inner_point(p):
                    self.attack_tri.append(tri.index)
                    self.attack_agents[i].tri_id = tri.index
                    break
        for tri in self.tris:
            if tri.index not in self.attack_tri:
                self.valid_area += tri.area
        for tri in self.tris:
            if tri.index not in self.attack_tri:
                n = round(self.pedestrian["number"] * tri.area / self.valid_area)
                if n > 0:
                    ps = generate_agent_in_triangle(tri, n, self.pedestrian["radius"])
                    for p in ps:
                        self.pedestrian_pos.append([p, tri.index])
        for i, p in enumerate(self.pedestrian_pos):
            print(p[0])
            self.tris[p[1]].append_pedestrian(i)
            self.pedestrian_agents.append(Agent(p[0], self.pedestrian["v_max"], self.pedestrian["v_max"], tri_id=p[1]))

    def run(self):
        self.init_attacker()
        self.init_pedestrian()
        lb, ob, ib = self.reader.get_basic_map()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.set_attacker_velocity()
        self.set_pedestrian_velocity()

        for tri in self.tris:
            # if tri.near_index != -1:
            #     ac = self.tris[tri.near_index].center
            #     xx = [tri.center.x, ac.x]
            #     yy = [tri.center.y, ac.y]
            #     plt.plot(xx, yy, color="red")
            # for pair in (tri.ls_A, tri.ls_B,tri.ls_C):
            #     xx = [pair.start.x, pair.end.x]
            #     yy = [pair.start.y, pair.end.y]
            #     plt.plot(xx, yy, color="red")
            plt.fill([tri.A.x, tri.B.x, tri.C.x, tri.A.x], [tri.A.y, tri.B.y, tri.C.y, tri.A.y], color="lavender")
        for item in lb:
            plt.plot(item[0], item[1], color='black', linewidth=1)
        for o in ob:
            self.ax.add_patch(o)
        xx, yy = [], []
        for i in ib:
            xx.append(i.x)
            yy.append(i.y)
        plt.fill(xx, yy, color="white")
        attacker_area = self.reader.get_attacker()
        for area in attacker_area:
            c_a = Circle(xy=(area["center"].x, area["center"].y), radius=area["radius"], color="yellow")
            self.ax.add_patch(c_a)
        p_A, a_A = [], []
        aw = []
        for agent in self.attack_agents:
            ag = Circle(xy=(agent.center.x, agent.center.y), radius=200, color="red")
            self.ax.add_patch(ag)
            arw = agent.plot("black")
            # self.ax.add_patch(arw)
            a_A.append(ag)
        for agent in self.pedestrian_agents:
            pg = Circle(xy=(agent.center.x, agent.center.y), radius=200, color='blue')
            self.ax.add_patch(pg)
            arw = agent.plot("black")
            # self.ax.add_patch(arw)
            aw.append(arw)
            p_A.append(pg)
        plt.xlim(30000, 600000)
        plt.ylim(30000, 335000)
        plt.axis("off")
        # self.set_attacker_velocity()
        # self.set_pedestrian_velocity()

        # def update(n):
        #     self.set_pedestrian_velocity()
        #     for idx, agt in enumerate(self.pedestrian_agents):
        #         # if aw[idx] is not None:
        #         #     aw[idx].remove()
        #         if not agt.is_shown:
        #             if p_A[idx]:
        #                 p_A[idx].remove()
        #                 p_A[idx] = None
        #             aw[idx] = None
        #             continue
        #         # aw[idx] = agt.plot("black")
        #         # self.ax.add_patch(aw[idx])
        #         p_A[idx].set_center((agt.center.x, agt.center.y))

        # self.ani = FuncAnimation(self.fig, update, frames=200, interval=150)
        plt.show()

    def set_attacker_velocity(self):
        for agent in self.attack_agents:
            dis = float("inf")
            idx = -1
            for i, ag in enumerate(self.pedestrian_agents):
                n_dis = math.sqrt((ag.center.x - agent.center.x) ** 2 + (ag.center.y - agent.center.y) ** 2)
                if n_dis < dis:
                    dis = n_dis
                    idx = i
            agent.v_now = Vector(self.pedestrian_agents[idx].center.x - agent.center.x, self.pedestrian_agents[idx].center.y - agent.center.y).normalize()

    def set_pedestrian_velocity(self):
        for agent in self.pedestrian_agents:
            if agent.tri_id == -1:
                agent.is_shown = False
                continue
            if not self.tris[agent.tri_id].is_inner_point(agent.center):
                self.update_triangle(agent)
            if self.tris[agent.tri_id].is_entrance:
                v = self.tris[agent.tri_id].eva_dir
                v_eva = Vector(v[0], v[1]).normalize()
                agent.next_step(v_eva.mul(300))
            else:
                t_id = self.tris[agent.tri_id].near_index
                ori = self.tris[agent.tri_id]
                tar = self.tris[t_id]
                common_line = ori.common_lineSegment(tar)
                cross_line = LineSegment(agent.center, tar.center)
                v_eva = common_line.evade_vector(agent.center)
                # if common_line.cross(cross_line.line.a, cross_line.line.b, cross_line.line.c):
                #     v_eva = Vector(tar.center.x - agent.center.x, tar.center.y - agent.center.y).normalize()
                # else:
                #     mid = Point((common_line.start.x + common_line.end.x) / 2,
                #                 (common_line.start.y + common_line.end.y) / 2)
                #     v_eva = Vector(mid.x - agent.center.x, mid.y - agent.center.y).normalize()
            agent.v_prf = v_eva
            agent.next_step(v_eva.mul(300))

    def update_triangle(self, agent):
        near_tri = []
        t_tri = self.tris[agent.tri_id]
        for p in (t_tri.A, t_tri.B, t_tri.C):
            for idx in self.point_map[p]:
                if idx not in near_tri:
                    near_tri.append(idx)
        for idx in near_tri:
            if self.tris[idx].is_inner_point(agent.center):
                agent.tri_id = idx
                return
        for tri in self.tris:
            if tri.is_inner_point(agent.center):
                agent.tri_id = idx
                return
        agent.tri_id = -1

    def find_nearest_pedestrian(self, agent):
        pass
