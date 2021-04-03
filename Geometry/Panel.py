from .Point import Point


class Panel:
    def __init__(self, A: [], B: [], C: []):
        a = [C[0] - A[0], C[1] - A[1], C[2] - A[2]]
        b = [B[0] - A[0], B[1] - A[1], B[2] - A[2]]
        self.A = a[1] * b[2] - b[1] * a[2]
        self.B = a[2] * b[0] - a[0] * b[2]
        self.C = a[0] * b[1] - b[0] * a[1]
        self.D = -self.A * A[0] - self.B * A[1] - self.C * A[2]

    def __str__(self):
        return "{}x + {}y + {}z + {} = 0".format(self.A, self.B, self.C, self.D)
