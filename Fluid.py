import numpy as np

VELOCITY_X = 0
VELOCITY_Y = 1

class Fluid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.velocity = np.zeros(shape=(width, height, 2))
        self.space = np.ones(shape=(width, height), dtype=np.int8)
        self.remainingTime = 0.0

    def solveIncompressibility(self):
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.space[x, y] == 0:
                    continue

                s = (self.space[x - 1, y] + self.space[x, y - 1]
                   + self.space[x + 1, y] + self.space[x, y + 1])

                if s == 0:
                    continue

                p = (self.velocity[x + 1, y, 0] - self.velocity[x, y, 0]
                   + self.velocity[x, y + 1, 1] - self.velocity[x, y, 1]) / -s

                overRelaxation = 1.9
                p *= overRelaxation

                self.velocity[x, y] -= np.array(self.space[x - 1, y], self.space[x, y - 1]) * p
                self.velocity[x + 1, y, 0] += self.space[x + 1, y] * p
                self.velocity[x, y + 1, 1] += self.space[x, y + 1] * p

    def extrapolate(self):
        for x in range(self.width):
            self.velocity[x, 0, 0] = self.velocity[x, 1, 0]
            self.velocity[x, -1, 0] = self.velocity[x, -2, 0]

        for y in range(self.height):
            self.velocity[0, y, 1] = self.velocity[1, y, 1]
            self.velocity[-1, y, 1] = self.velocity[-2, y, 1]

    def advectVelocity(self, dt):
        for y in range(1, self.height):
            for x in range(1, self.width):
                if self.space[x, y] and self.space[x - 1, y] and y < self.height - 1:
                    pass

                if self.space[x, y] and self.space[x, y - 1] and x < self.width - 1:
                    pass

    def simulate(self, dt):
        stepsPerSecond = 100

        steps = int((dt + self.remainingTime) * stepsPerSecond)
        self.remainingTime = (dt + self.remainingTime) - steps / stepsPerSecond

        for i in range(steps):
            self.solveIncompressibility()
        self.extrapolate()
        self.advectVelocity(dt)

    def sampleField(self, x, y, field):
        x = max(1.0, min(x, self.width))
        y = max(1.0, min(y, self.height))

        if field == VELOCITY_X:
            dx = 0.5
            dy = 0.0
        elif field == VELOCITY_Y:
            dx = 0.0
            dy = 0.5

        x0 = int((x - dx) // (self.width - 1))
        tx = (x - dx) - x0
        x1 = min(x0 + 1, self.width - 1)

        y0 = int((y - dy) // (self.height - 1))
        ty = (y - dy) - y0
        y1 = min(y0 + 1, self.height - 1)

        sx = 1.0 - tx
        sy = 1.0 - ty

        if field == VELOCITY_X:
            return (sx*sy * self.velocity[x0 * self.height, y0, 0] +
                    tx*sy * self.velocity[x1 * self.height, y0, 0] +
                    tx*ty * self.velocity[x1 * self.height, y1, 0] +
                    sx*ty * self.velocity[x0 * self.height, y1, 0])
        elif field == VELOCITY_Y:
            return (sx*sy * self.velocity[x0 * self.height, y0, 1] +
                    tx*sy * self.velocity[x1 * self.height, y0, 1] +
                    tx*ty * self.velocity[x1 * self.height, y1, 1] +
                    sx*ty * self.velocity[x0 * self.height, y1, 1])

    def sampleVelocity(self, x, y):
        return (
            self.sampleField(x, y, VELOCITY_X),
            self.sampleField(x, y, VELOCITY_Y)
        )
