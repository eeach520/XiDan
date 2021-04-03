from matplotlib.patches import Arc, Ellipse, Circle
import dxfgrabber
import shelve
from Geometry.Point import Point
from Geometry.Line import Line
from Geometry.LineSegment import LineSegment
from Geometry.Triangle import Triangle
import heapq
import math


class node:
    def __init__(self, tri_id, tri_dis):
        self.tri_id, self.tri_dis = tri_id, tri_dis

    def __lt__(self, other):
        return self.tri_dis < other.tri_dis


class DXFReader:
    def __init__(self):
        self.head = [-1] * 400
        self.edge = [0] * 3000
        self.next_edge = [0] * 3000
        self.weight = [0] * 3000
        self.points = []  #
        self.tris = []  # 三角划分结果
        self.centers = []
        self.index = 0
        self.counter = 0
        self.lines = []
        self.point_map = {}
        self.border_points_group = [[0, 76], [71, 116], [67, 77], [115, 41], [117, 108]]
        self.attack_area = []
        self.angle = [[311 + 90, 346 + 90], [13 + 90, 167 + 90], [215 + 90, 270 + 90]]
        self.jj = 0
        self.color_ob = []
        self.inner_job = []
        self.basic_line_border = []
        self.init()

    def get_tri_edges(self):
        dxf = dxfgrabber.readfile("raw/xidan_final_1.dxf")
        for e in dxf.entities:
            if e.dxftype == 'LINE':
                if e.color in (18, 242, 5, 215, 1):
                    line = LineSegment(Point(int(e.start[0]), int(e.start[1])), Point(int(e.end[0]), int(e.end[1])))
                    is_border = e.color in (18, 242, 1)
                    self.lines.append([line, is_border])
                x = [e.start[0], e.end[0]]
                y = [e.start[1], e.end[1]]
                if e.color in (256, 114, 18, 215, 242):
                    self.basic_line_border.append([x, y])
            elif e.dxftype == 'CIRCLE' and e.color in (18, 242):
                head = Arc(xy=(e.center[0], e.center[1]),  # 椭圆中心，（圆弧是椭圆的一部分而已）
                           width=e.radius * 2,  # 长半轴
                           height=e.radius * 2,  # 短半轴
                           theta1=0,  # 圆弧起点处角度
                           theta2=360,  # 圆弧终点处角度
                           facecolor='blue',  # 填充色
                           ec='black',  # 边框颜色
                           linewidth=1
                           )
                ob = Circle(xy=(e.center[0], e.center[1]), radius=e.radius, ec="white", fc="white", fill=True,
                            linewidth=1)
                self.color_ob.append(ob)
                self.color_ob.append(head)
            elif e.dxftype == 'ELLIPSE' and e.color in (18, 242):
                h = e.major_axis[0] + e.major_axis[1]
                w = h * e.ratio
                head = Arc(xy=(e.center[0], e.center[1]),  # 椭圆中心，（圆弧是椭圆的一部分而已）
                           width=w * 2,  # 长半轴
                           height=h * 2,  # 短半轴
                           theta1=self.angle[self.jj][0],  # 圆弧起点处角度
                           theta2=self.angle[self.jj][1],  # 圆弧终点处角度
                           color='blue',  # 填充色
                           ec='black',  # 边框颜色
                           linewidth=1
                           )
                ob = Ellipse(xy=(e.center[0], e.center[1]),  # 椭圆中心，（圆弧是椭圆的一部分而已）
                             width=w * 2,  # 长半轴
                             height=h * 2,  # 短半轴)
                             ec="lavender",
                             fc="lavender",
                             linewidth=1
                             )
                self.color_ob.append(ob)
                self.color_ob.append(head)
                self.jj += 1
            elif e.dxftype == 'ARC' and e.color in (18, 242):
                head = Arc(xy=(e.center[0], e.center[1]),  # 椭圆中心，（圆弧是椭圆的一部分而已）
                           width=e.radius * 2,  # 长半轴
                           height=e.radius * 2,  # 短半轴
                           theta1=e.start_angle,  # 圆弧起点处角度
                           theta2=e.end_angle,  # 圆弧终点处角度
                           facecolor='blue',  # 填充色
                           ec='black',  # 边框颜色
                           linewidth=1
                           )
                ob = Circle(xy=(e.center[0], e.center[1]), radius=e.radius, ec="lavender", fc="lavender", fill=True,
                            linewidth=1)
                if e.color == 18:
                    self.color_ob.append(ob)
                self.color_ob.append(head)
        self.sort_color()
        at_dxf = dxfgrabber.readfile("raw/xidan-plus.dxf")
        inner = []
        for e in at_dxf.entities:
            if e.dxftype == 'CIRCLE' and e.color == 240:
                self.attack_area.append({"center": Point(e.center[0], e.center[1]), "radius": e.radius})
            if e.dxftype == 'LINE' and e.color == 141:
                inner.append([Point(e.start[0], e.start[1]), Point(e.end[0], e.end[1])])
        self.find_inner(inner)

    def find_inner(self, li):
        res = [li[0][0], li[0][1]]
        for i in range(7):
            res.append(li[i + 1][1])
        res.append(res[0])
        self.inner_job = res

    def sort_color(self):
        container = []
        for i in range(len(self.color_ob) - 1, -1, -1):
            if not isinstance(self.color_ob[i], Arc):
                container.append(self.color_ob[i])
        for b in self.color_ob:
            if isinstance(b, Arc):
                container.append(b)
        self.color_ob = container

    def parse_tri_from_lines(self):
        memo = {}
        for line, is_border in self.lines:
            P = [line.start, line.end]
            for p in P:
                if p not in self.points:
                    self.points.append(p)
        for idx, point in enumerate(self.points):
            self.point_map[point] = []
            memo[point] = idx
        for line, is_border in self.lines:
            p1, p2 = line.start, line.end
            i1, i2 = memo[p1], memo[p2]
            if i1 is None or i2 is None:
                raise Exception("Dictionary key is none!")
            self.add(i1, i2, is_border)
            self.add(i2, i1, is_border)
        for i in range(len(self.points)):
            self.dfs([i], -1, 1)
        for i, t in enumerate(self.tris):
            for pp in [t.A, t.B, t.C]:
                self.point_map[pp].append(i)

    def add(self, start, end, w):
        if w:
            weight = 1
        else:
            weight = 0
        self.edge[self.index] = end
        self.weight[self.index] = weight
        self.next_edge[self.index] = self.head[start]
        self.head[start] = self.index
        self.index += 1

    def dfs(self, seq: [], ori: int, cnt: int):
        if cnt == 4:
            if seq[0] == seq[3]:
                t = Triangle(self.points[seq[0]], self.points[seq[1]], self.points[seq[2]], self.counter)
                if t.center not in self.centers:
                    for item in self.border_points_group:
                        if item[0] in seq and item[1] in seq:
                            bLine = LineSegment(self.points[item[0]], self.points[item[1]])
                            a, b = bLine.b, -bLine.a
                            c = - (a * t.center.x + b * t.center.y)
                            if bLine.cross(a, b, c):
                                pp = bLine.line.cross(a=a, b=b, c=c)
                                eva_dir = [pp.x - t.center.x, pp.y - t.center.y]
                            else:
                                pp = Point((self.points[item[0]].x + self.points[item[1]].x) / 2,
                                           (self.points[item[0]].y + self.points[item[1]].y) / 2)
                                eva_dir = [pp.x - t.center.x, pp.y - t.center.y]
                            eva_dis = bLine.distance(t.center)
                            t = Triangle(self.points[seq[0]], self.points[seq[1]], self.points[seq[2]], self.counter,
                                         is_entrance=True,
                                         eva_dir=eva_dir,
                                         min_eva_dis=eva_dis)
                            print("this index is {}, dir is {}, dis is {}".format(self.counter, eva_dir, eva_dis))
                    self.centers.append(t.center)
                    self.tris.append(t)
                    self.counter += 1

            return
        start = self.head[seq[cnt - 1]]
        while start != -1:
            if start != ori:
                e = self.edge[start]
                seq.append(e)
                self.dfs(seq, seq[cnt - 1], cnt + 1)
                seq.pop()
            start = self.next_edge[start]

    def get_near_tri(self, i: int):
        res = []
        for it in [[self.tris[i].A, self.tris[i].B], [self.tris[i].A, self.tris[i].C],
                   [self.tris[i].C, self.tris[i].B]]:
            a = self.point_map[it[0]]
            b = self.point_map[it[1]]
            c = [j for j in a if j in b]
            for t in c:
                if t not in res:
                    res.append(t)
        return res

    def get_tris_through_two_points(self, p1: Point, p2: Point):
        a = self.point_map[p1]
        b = self.point_map[p2]
        return [j for j in a if j in b]

    def update_border_in_tris(self):
        for line, is_border in self.lines:
            if is_border:
                tris = self.get_tris_through_two_points(line.start, line.end)
                if len(tris) == 0:
                    continue
                st = {line.start, line.end}
                for i in tris:
                    if {self.tris[i].B, self.tris[i].C} == st:
                        self.tris[i].bA = True
                    elif {self.tris[i].A, self.tris[i].C} == st:
                        self.tris[i].bB = True
                    elif {self.tris[i].A, self.tris[i].B} == st:
                        self.tris[i].bC = True
                    else:
                        print("warning , not border found")

    def dijkstra(self):
        mask = [False] * len(self.tris)
        idx_list = []
        for i, tri in enumerate(self.tris):
            if tri.is_entrance:
                idx_list.append(i)
        heap = []
        for idx in idx_list:
            heapq.heappush(heap, node(idx, self.tris[idx].min_eva_dis))
        while len(heap) > 0:
            n = heapq.heappop(heap)
            if mask[n.tri_id]:
                continue
            mask[n.tri_id] = True
            for i in self.get_near_tri(n.tri_id):
                if not mask[i]:
                    dx = (self.tris[i].center.x - self.tris[n.tri_id].center.x)
                    dy = (self.tris[i].center.y - self.tris[n.tri_id].center.y)
                    dd = math.sqrt(dx * dx + dy * dy) + self.tris[n.tri_id].min_eva_dis
                    if dd < self.tris[i].min_eva_dis:
                        self.tris[i].min_eva_dis = dd
                        self.tris[i].near_index = n.tri_id
                        heapq.heappush(heap, node(i, self.tris[i].min_eva_dis))

    def init(self):
        self.get_tri_edges()
        self.parse_tri_from_lines()
        self.update_border_in_tris()
        self.dijkstra()

    def get_attacker(self):
        return self.attack_area

    def get_tris(self):
        return self.tris

    def get_point_map(self):
        return self.point_map

    def get_basic_map(self):
        return self.basic_line_border, self.color_ob, self.inner_job
