from DXF.DXFReader import DXFReader
from DXF.DXFReader import node
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
import heapq
import numpy as np
import random


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
        self.r_view = 90000
        self.r_panic = 5000
        self.hurt_radius = 600

    def init_attacker(self):
        attacker_area = self.reader.get_attacker()
        for area in attacker_area:
            arc = Arc(Point(area["center"].x, area["center"].y), area["radius"])
            self.attack_pos += generate_agent_in_circle(arc, self.attack["number"] / len(attacker_area),
                                                        self.attack["radius"])
        for i, p in enumerate(self.attack_pos):
            self.attack_agents.append(Agent(p, self.attack["radius"], i, 'attacker', self.attack["v_max"]))
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
            self.tris[p[1]].append_pedestrian(i)
            self.pedestrian_agents.append(
                Agent(p[0], self.pedestrian["radius"], i, "pedestrian", self.pedestrian["v_max"], tri_id=p[1]))

    def run(self):
        self.init_attacker()
        self.init_pedestrian()
        lb, ob, ib = self.reader.get_basic_map()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        for tri in self.tris:
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
        pw = [None] * 10
        for agent in self.attack_agents:
            ag = Circle(xy=(agent.center.x, agent.center.y), radius=200, color="red")
            self.ax.add_patch(ag)
            a_A.append(ag)
        for agent in self.pedestrian_agents:
            pg = Circle(xy=(agent.center.x, agent.center.y), radius=200, color='blue')
            self.ax.add_patch(pg)
            arw = agent.plot("black")
            self.ax.add_patch(arw)
            aw.append(arw)
            p_A.append(pg)
        plt.xlim(30000, 600000)
        plt.ylim(30000, 335000)
        plt.axis("off")

        def update(n):
            self.set_pedestrian_velocity()
            self.set_attacker_velocity()
            for idx, agt in enumerate(self.pedestrian_agents):
                if aw[idx] is not None:
                    aw[idx].remove()
                    aw[idx] = None
                if not agt.is_shown or not agt.is_alive:
                    if p_A[idx]:
                        p_A[idx].remove()
                        p_A[idx] = None
                    aw[idx] = None
                    continue
                aw[idx] = agt.plot("black")
                self.ax.add_patch(aw[idx])
                p_A[idx].set_center((agt.center.x, agt.center.y))
            for idx, agt in enumerate(self.attack_agents):
                if len(pw) > idx and pw[idx] is not None:
                    pw[idx].remove()
                arw = agt.plot("black")
                self.ax.add_patch(arw)
                pw[idx] = arw
                a_A[idx].set_center((agt.center.x, agt.center.y))

        self.ani = FuncAnimation(self.fig, update, frames=200, interval=400, repeat=False)
        plt.show()

    def set_attacker_velocity(self):
        for agent in self.attack_agents:
            self.find_nearest_pedestrian(agent)
            if not self.tris[agent.tri_id].is_inner_point(agent.center):
                self.update_triangle(agent)
            self.kill_pedestrian(agent)

    def kill_pedestrian(self, agent):
        for agt in self.pedestrian_agents:
            dx = agt.center.x - agent.center.x
            dy = agt.center.y - agent.center.y
            d = math.sqrt(dx ** 2 + dy ** 2)
            if d < self.hurt_radius:
                agt.is_alive = False
                agt.is_shown = False

    def set_pedestrian_velocity(self):
        for agent in self.pedestrian_agents:
            if agent.tri_id == -1 or not agent.is_alive:
                agent.is_shown = False
                continue
            if self.tris[agent.tri_id].is_entrance:
                v = self.tris[agent.tri_id].eva_dir
                v_eva = Vector(v[0], v[1]).normalize()
            else:
                t_id = self.tris[agent.tri_id].near_index
                ori = self.tris[agent.tri_id]
                tar = self.tris[t_id]
                common_line = ori.common_lineSegment(tar)
                v_eva = common_line.evade_vector(agent.center)
            # v_eva = self.get_pedestrian_compose_velocity(agent, v_eva)
            agent.v_prf = v_eva
            agent.next_step(v_eva.mul(300))
            if not self.tris[agent.tri_id].is_inner_point(agent.center):
                self.update_triangle(agent)

    def get_pedestrian_compose_velocity(self, agent, e_eva):
        part1 = Vector(0, 0)
        part2 = Vector(0, 0)
        for agt in self.attack_agents:
            dx = agt.center.x - agent.center.x
            dy = agt.center.y - agent.center.y
            dis = math.sqrt(dx ** 2 + dy ** 2)
            base = Vector(agent.center.x - agt.center.x, agent.center.y - agt.center.y)
            if dis <= self.r_panic:
                n_p = base.mul(40000).div(dis)
                part1 = Vector.add(part1, n_p)
            elif dis <= self.r_view:
                n_p = base.mul(40000).div(dis ** 2)
                part2 = Vector.add(part2, n_p)
        v_compose = Vector.add(part1, part2)
        v_final = Vector.add(v_compose, e_eva).normalize()
        return v_final

    def update_triangle(self, agent):
        near_tri = []
        t_tri = self.tris[agent.tri_id]
        for p in (t_tri.A, t_tri.B, t_tri.C):
            for idx in self.point_map[p]:
                if idx not in near_tri:
                    near_tri.append(idx)
        for idx in near_tri:
            if self.tris[idx].is_inner_point(agent.center):
                if agent.a_type == "pedestrian":
                    self.tris[agent.tri_id].remove_pedestrian(agent.id)
                    self.tris[idx].append_pedestrian(agent.id)
                else:
                    self.tris[agent.tri_id].remove_attacker(agent.id)
                    self.tris[idx].append_attacker(agent.id)
                agent.tri_id = idx
                return
        for tri in self.tris:
            if tri.is_inner_point(agent.center):
                agent.tri_id = tri.index
                return
        agent.tri_id = -1

    def find_nearest_pedestrian(self, agent):
        tri_id = agent.tri_id
        mask = [False] * len(self.tris)
        tri_index = [-1] * len(self.tris)
        dis_list = [float("inf")] * len(self.tris)
        idx_list = [tri_id]
        dis_list[tri_id] = 0
        heap = []
        for idx in idx_list:
            heapq.heappush(heap, node(idx, 0))
        distance = float("inf")
        target_id = -1
        target_tri_id = -1
        while len(heap) > 0:
            n = heapq.heappop(heap)
            id = n.tri_id
            if mask[id]:
                continue
            mask[id] = True
            valid_list = []
            for ag_id in self.tris[id].pedestrian_list:
                if self.pedestrian_agents[ag_id].is_alive:
                    valid_list.append(ag_id)
            if len(valid_list) > 0:
                target_tri_id = id
                for idx in valid_list:
                    dis = math.sqrt((self.pedestrian_agents[idx].center.x - agent.center.x) ** 2 +
                                    (self.pedestrian_agents[idx].center.y - agent.center.y) ** 2)
                    if dis < distance:
                        distance, target_id = dis, idx
                break
            for i in self.find_near_tris(id):
                if not mask[i]:
                    dx = (self.tris[i].center.x - self.tris[n.tri_id].center.x)
                    dy = (self.tris[i].center.y - self.tris[n.tri_id].center.y)
                    dd = math.sqrt(dx * dx + dy * dy) + dis_list[id]
                    if dd < dis_list[i]:
                        dis_list[i] = dd
                        tri_index[i] = id
                        heapq.heappush(heap, node(i, dd))
        if target_tri_id == agent.tri_id:
            cha_v = Vector(self.pedestrian_agents[target_id].center.x - agent.center.x,
                           self.pedestrian_agents[target_id].center.y - agent.center.y).normalize()
        else:
            while tri_index[target_tri_id] != tri_id:
                target_tri_id = tri_index[target_tri_id]
            common_line = self.tris[tri_id].common_lineSegment(self.tris[target_tri_id])
            cha_v = common_line.evade_vector(agent.center).normalize()
        agent.next_step(cha_v.mul(350))

    def find_near_tris(self, tri_id):
        res = []
        for it in [[self.tris[tri_id].A, self.tris[tri_id].B], [self.tris[tri_id].A, self.tris[tri_id].C],
                   [self.tris[tri_id].C, self.tris[tri_id].B]]:
            a = self.point_map[it[0]]
            b = self.point_map[it[1]]
            c = [j for j in a if j in b]
            for t in c:
                if t not in res:
                    res.append(t)
        return res
