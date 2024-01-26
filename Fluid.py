import numpy as np

class Fluid:
    def __init__(self, numX, numY):
        self.velocity = np.zeros(shape=(numX, numY, 2))
        self.space = np.zeros(shape=(numX, numY))

        for y in range(self.lev_h):
            for x in range(self.lev_w):
                self.space[x, y] = 0.0 if self.level[y][x] == '#' else 1.0
