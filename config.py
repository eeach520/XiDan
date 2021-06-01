from RVO.LP2D import LP2D_solution

from Geometry.Vector import Vector
from Geometry.Point import Point
from Geometry.Arc import Arc
from RVO.LP3D import LP3D_solution
from DXF.DXFReader import DXFReader
import matplotlib.pyplot as plt
from scene.Random import generate_agent_in_circle, generate_agent_in_triangle
from matplotlib.patches import Circle
from Geometry.Triangle import Triangle
from scene.Evacuation import Evacuation

# a = DXFReader()
# a.get_attacker()
# plt.show()
# a = {Point(3, 4), Point(5, 6)}
# b = {Point(5, 6), Point(3, 4)}
#
# # print(a == b)
# print(round(2.00))

e = Evacuation({"number": 10, "radius": 200, "v_max": 10}, {"number": 1000, "radius": 200, "v_max": 10})
# e.run()
# e.d_run()
e.fake()