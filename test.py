from Geometry.Point import Point
from Geometry.LineSegment import LineSegment
from Geometry.Line import Line
from Geometry.Arc import Arc
from Geometry.Vector import Vector
from math import pi, acos, sqrt, cos, sin
from Geometry.Panel import Panel
import numpy as np

from RVO.LP2D import LP2D_solution

from RVO.LP3D import LP3D_solution, convert_to_2D

# p = [Panel([1, 0, 0], [0, 1, 0], [0, 0, 1])
#     , Panel([-1, 0, 0], [0, 1, 0], [0, 0, 1])
#     , Panel([1, 0, 0], [0, -1, 0], [0, 0, 1])
#     , Panel([-1, 0, 0], [0, -1, 0], [0, 0, 1])
#     , Panel([1, 0, 0], [0, 1, 0], [0, 0, -1])
#     , Panel([-1, 0, 0], [0, 1, 0], [0, 0, -1])
#     , Panel([1, 0, 0], [0, -1, 0], [0, 0, -1])
#     , Panel([-1, 0, 0], [0, -1, 0], [0, 0, -1])]
# border = []
# for pp in p:
#     b = [pp.A, pp.B, pp.C, pp.D]
#     if pp.D > 0:
#         b = [-pp.A, -pp.B, -pp.C, -pp.D]
#     border.append(b)
# c = 0
# for i in range(1000):
#     stat, res = LP3D_solution(border, [1,0,0], 8)
#     # print(res)
#     if abs(res[3] - 1) > 0.5:
#         c += 1
# print(c)
from RVO.Agent import Agent
from RVO.ORCA import update
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse, Circle, Arrow
import matplotlib.colors as mcolors

colors = list(mcolors.TABLEAU_COLORS.keys())
print(len(colors))

r = 5
v_max = 8

xx = np.linspace(-100, 100, 8)
hi = []
li = []
agents = []
for pp in xx:
    hi.append(Point(pp, 90))
    li.append(Point(pp, -90))
# for i in range(len(li)):
#     agents.append(Agent(li[i], hi[len(li) - i - 1], r, v_max))
agents += [
    Agent(Point(80, 0), Point(-80, 0), r, v_max),
    Agent(Point(-80, 0), Point(80, 0), r, v_max),
    Agent(Point(5, 90), Point(5, -80), r, v_max),
    # Agent(Point(-10, -80), Point(-10, 80), r, v_max)
    # , Agent(Point(80, 80), Point(-80, -80), r, v_max)
    # , Agent(Point(-80, -80), Point(80, 80), r, v_max)
    # , Agent(Point(-83, 86), Point(80, -80), r, v_max)
    # , Agent(Point(80, -80), Point(-80, 80), r, v_max)
    # , Agent(Point(40, -80), Point(-40, 80), r, v_max)
]

cirs = []
xp = []
yp = []
aw = []
fig = plt.figure()
ax = fig.add_subplot(111)
for index, agent in enumerate(agents):
    cirs.append(
        Circle(xy=(agent.center.x, agent.center.y), radius=agent.r, color=mcolors.TABLEAU_COLORS[colors[index % 10]]))
    xp.append([agent.center.x])
    yp.append([agent.center.y])
    dd = agent.plot()
    aa = Arrow(dd[0], dd[1], dd[2], dd[3], width=1)
    aw.append(ax.add_patch(aa))

# plt.plot([-30, 50], [5, 5])
ob = LineSegment(Point(-30, 5), Point(50, 5))
for cir in cirs:
    ax.add_patch(cir)
plt.xlim(-120, 120)
plt.ylim(-100, 100)

f = []
for i in range(len(agents)):
    fi, = plt.plot(xp[i], yp[i], color=mcolors.TABLEAU_COLORS[colors[i % 10]])
    f.append(fi)


def updates(n):
    v = []
    for index, item in enumerate(agents):
        b = agents[:index]
        c = agents[index + 1:]
        v.append(update(item, b + c, [], 3, v_max))
    for index, vv in enumerate(v):
        agents[index].next_step(vv)
        d = agents[index].plot()
        # ax.add_patch(d)
        cirs[index].set_center((agents[index].center.x, agents[index].center.y))
        # aw[index].update(d[0],d[1],d[2],d[3])
        aw[index].remove()
        aw[index] = ax.add_patch(Arrow(d[0], d[1], d[2], d[3], color='black', width=2))
        # xp[index].append(agents[index].center.x)
        # yp[index].append(agents[index].center.y)
        # f[index].set_data(xp[index], yp[index])
    return


ani = FuncAnimation(fig, updates, frames=50, interval=150)
plt.show()
# extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
# ani.save('move.gif')
