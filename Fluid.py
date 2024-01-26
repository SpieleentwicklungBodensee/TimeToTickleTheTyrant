import numpy as np

class Fluid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.velocity = np.zeros(shape=(width, height, 2))
        self.space = np.zeros(shape=(width, height))

    def solveIncompressibility(self):
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.space[x, y] == 0.0:
                    continue

                s = (self.space[x - 1, y] + self.space[x, y - 1]
                   + self.space[x + 1, y] + self.space[x, y + 1])

                if s == 0.0:
                    continue

                p = (self.velocity[x + 1, y, 0] - self.velocity[x, y, 0]
                   + self.velocity[x, y + 1, 1] - self.velocity[x, y, 1]) / -s

                overRelaxation = 1.9
                p *= overRelaxation

                self.velocity[x, y] -= np.array(self.space[x - 1, y], self.space[x, y - 1]) * p
                self.velocity[x + 1, y, 0] += self.space[x + 1, y] * p
                self.velocity[x, y + 1, 1] += self.space[x, y + 1] * p

    def simulate(self, dt):
        for i in range(100):
            self.solveIncompressibility()
        #self.extrapolate()
        #self.advectVelocity()
