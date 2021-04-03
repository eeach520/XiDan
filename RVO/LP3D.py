"""
linear programming in 3-D space
"""
from Geometry.Vector import Vector
from .LP2D import LP2D_solution
import random
import math
import numpy as np


def LP3D_solution(pl: [], f: [], M: float):
    """
    plane vertical to XoY is not good
    :param pl:
    :param f:
    :param M:
    :return:
    """
    for p in pl:
        if abs(p[2]) < 1e-9:
            p[2] = max(p[0], p[1]) / 10000
    return random_bounded_LP3D(pl, f, M)


def random_bounded_LP3D(pl: [], f: [], M: float):
    random.shuffle(pl)
    borders, v = init(f, M)
    for p in pl:
        if p[0] * v[0] + p[1] * v[1] + p[2] * v[2] + p[3] <= 1e-5:  # 满足条件则不做处理
            borders.append(p)
            continue
        stat, v = convert_to_2D(borders, p, f, M)
        if not stat:
            return False, None
        borders.append(p)
    return True, v


def convert_to_2D(borders: [], p: [], f: [], M: float):
    """
    change axis, get projection, call 2D function
    :param M:
    :param f:
    :param borders:
    :param p:
    :return:
    """
    r_p, r_pos, r_neg = get_rotate_matrix(p)
    r_f = [[
        f[0] * r_neg[0][0] + f[1] * r_neg[0][1] + f[2] * r_neg[0][2],
        f[0] * r_neg[1][0] + f[1] * r_neg[1][1] + f[2] * r_neg[1][2],
        f[0] * r_neg[2][0] + f[1] * r_neg[2][1] + f[2] * r_neg[2][2],
        f[0] * r_neg[3][0] + f[1] * r_neg[3][1] + f[2] * r_neg[3][2]
    ]]
    r_z = -r_p[0][3] / r_p[0][2]
    r_borders = get_project_borders(borders, r_neg, r_z)
    factor = Vector(r_f[0][0], r_f[0][1])
    stat1, res1 = LP2D_solution(r_borders, factor, M * 1000)
    stat2, res2 = LP2D_solution(r_borders, factor.mul(-1), M * 1000)
    if not stat1 or not stat2:
        return False, None
    r1 = [res1.x, res1.y, r_z, 1]
    r2 = [res2.x, res2.y, r_z, 1]
    v1 = np.array([r1[:]]) @ r_neg
    v2 = np.array([r2[:]]) @ r_neg
    v1[0][3] = v1[0][0] * f[0] + v1[0][1] * f[1] + v1[0][2] * f[2]
    v2[0][3] = v2[0][0] * f[0] + v2[0][1] * f[1] + v2[0][2] * f[2]
    v = None
    vs = -float("inf")
    for vvv in [v1, v2]:
        if vvv[0][3] > vs:
            vs = vvv[0][3]
            v = vvv
    return True, list(v[0])


def get_project_borders(borders: [], r_neg, z: float):
    """
    deal with less equal than <= 
    :param r_neg: 
    :param borders: 
    :param z: 
    :return: 
    """
    r_borders = []
    for border in borders:
        r_borders.append([
            border[0] * r_neg[0][0] + border[1] * r_neg[0][1] + border[2] * r_neg[0][2],
            border[0] * r_neg[1][0] + border[1] * r_neg[1][1] + border[2] * r_neg[1][2],
            border[0] * r_neg[2][0] + border[1] * r_neg[2][1] + border[2] * r_neg[2][2],
            border[3] + border[0] * r_neg[3][0] + border[1] * r_neg[3][1] + border[2] * r_neg[3][2]
        ])
    c_borders = []
    for border in r_borders:
        if abs(border[0]) > 1e-9 or abs(border[1]) > 1e-9:
            c_borders.append([border[0], border[1], border[2] * z + border[3]])
    return c_borders


def get_rotate_matrix(p: []):
    """
    rotate along z axis, then rotate along x according to the angle
    :param n: 
    :param p:
    :return:
    """
    n = get_inner_normal(p)
    sin1 = n[0] / math.sqrt(n[0] ** 2 + n[1] ** 2)
    cos1 = n[1] / math.sqrt(n[0] ** 2 + n[1] ** 2)
    z = np.array([
        [cos1, sin1, 0, 0],
        [-sin1, cos1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    inv_z = np.linalg.inv(z)
    rotated_z = [[
        p[0] * inv_z[0][0] + p[1] * inv_z[0][1] + p[2] * inv_z[0][2],
        p[0] * inv_z[1][0] + p[1] * inv_z[1][1] + p[2] * inv_z[1][2],
        p[0] * inv_z[2][0] + p[1] * inv_z[2][1] + p[2] * inv_z[2][2],
        p[3] + p[0] * inv_z[3][0] + p[1] * inv_z[3][1] + p[2] * inv_z[3][2]
    ]]
    n2 = get_inner_normal(rotated_z[0])
    sin2 = n2[1] / math.sqrt(n2[1] ** 2 + n2[2] ** 2)
    cos2 = n2[2] / math.sqrt(n2[1] ** 2 + n2[2] ** 2)
    x = np.array([
        [1, 0, 0, 0],
        [0, cos2, sin2, 0],
        [0, -sin2, cos2, 0],
        [0, 0, 0, 1]
    ])
    inv_x = np.linalg.inv(x)
    rotated_x = [[
        rotated_z[0][0] * inv_x[0][0] + rotated_z[0][1] * inv_x[0][1] + rotated_z[0][2] * inv_x[0][2],
        rotated_z[0][0] * inv_x[1][0] + rotated_z[0][1] * inv_x[1][1] + rotated_z[0][2] * inv_x[1][2],
        rotated_z[0][0] * inv_x[2][0] + rotated_z[0][1] * inv_x[2][1] + rotated_z[0][2] * inv_x[2][2],
        rotated_z[0][3] + rotated_z[0][0] * inv_x[3][0] + rotated_z[0][1] * inv_x[3][1] + rotated_z[0][2] * inv_x[3][2]
    ]]
    pos, neg = z @ x, inv_x @ inv_z
    return rotated_x, pos, neg


def get_inner_normal(p: []):
    base = [0, 0, 0]
    for i in range(3):
        if abs(p[i]) > 1e-9:
            base[i] = -p[3] / p[i]
            break
    candi = [p[0], p[1], p[2]]
    test_p = [base[0] + candi[0], base[1] + candi[1], base[2] + candi[2]]
    if test_p[0] * p[0] + test_p[1] * p[1] + test_p[2] * p[2] + p[3] > 0:
        candi = [-candi[0], -candi[1], -candi[2]]
    return candi
    

def init(f: [], M: float):
    v, target = None, -float("inf")
    borders = [[1, 0, 0, -M], [-1, 0, 0, -M], [0, 1, 0, -M], [0, -1, 0, -M], [0, 0, 1, -M * 1000], [0, 0, -1, -M * 1000]]
    for i in range(8):
        b = [M, M, M]
        for j in range(3):
            if (1 << j) & i > 0:
                b[j] *= -1
        if f[0] * b[0] + f[1] * b[1] + f[2] * b[2] > target:
            v, target = b, f[0] * b[0] + f[1] * b[1] + f[2] * b[2]
    return borders, v
