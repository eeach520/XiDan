class Point:
    """
    point in 2-D space
    """

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def __hash__(self):
        return hash(str(self.x) + str(self.y))

    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-2 and abs(self.y - other.y) < 1e-2

    def __str__(self):
        return "({},{})".format(self.x, self.y)
