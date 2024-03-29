# cython: language_level=3

import numpy as np

from libc.math cimport floor, sqrt, round

cimport cython
from libc.stdint cimport int8_t, uint32_t

VELOCITY_X = 0
VELOCITY_Y = 1
SMOKE = 2

cdef class Fluid:
    cdef int granularity
    cdef int width
    cdef int height
    cdef double[:, :, ::1] velocity
    cdef int8_t[:, ::1] space
    cdef double[:, ::1] smoke
    cdef double remainingTime

    def __init__(self, width, height, granularity):
        self.granularity = granularity
        self.width = width * granularity + 2
        self.height = height * granularity + 2
        self.velocity = np.zeros(shape=(self.width, self.height, 2))
        self.space = np.ones(shape=(self.width, self.height), dtype=np.int8)
        self.smoke = np.zeros(shape=(self.width, self.height))
        self.remainingTime = 0.0

    cdef float conv_coord(self, float v):
        return v * self.granularity + 1

    def setSpace(self, int x, int y, s):
        x0 = x * self.granularity + 1 - self.granularity // 2
        y0 = y * self.granularity + 1 - self.granularity // 2

        for dx in range(self.granularity):
            for dy in range(self.granularity):
                self.space[x0 + dx, y0 + dx] = s

    def setBlockVelocity(self, int x, int y, v):
        x0 = x * self.granularity + 1
        y0 = y * self.granularity + 1

        for dx in range(self.granularity + 1):
            for dy in range(self.granularity + 1):
                self.velocity[x0 + dx, y0 + dy, 0] = v[0]
                self.velocity[x0 + dx, y0 + dy, 1] = v[1]

    def setVelocity(self, float x_, float y_, v):
        v *= self.granularity

        cdef int x = <int>floor(self.conv_coord(x_) + 0.5)
        cdef int y = <int>floor(self.conv_coord(y_))
        self.velocity[x, y, 0] = v[0]

        x = <int>floor(self.conv_coord(x_))
        y = <int>floor(self.conv_coord(y_) + 0.5)
        self.velocity[x, y, 1] = v[1]

    cdef solveIncompressibility(self):
        cdef int x, y, s

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
                #p *= overRelaxation

                self.velocity[x, y, 0] -= self.space[x - 1, y] * p
                self.velocity[x + 1, y, 0] += self.space[x + 1, y] * p
                self.velocity[x, y, 1] -= self.space[x, y - 1] * p
                self.velocity[x, y + 1, 1] += self.space[x, y + 1] * p

    cdef extrapolate(self):
        cdef int x
        for x in range(self.width):
            self.velocity[x, 0, 0] = self.velocity[x, 1, 0]
            self.velocity[x, -1, 0] = self.velocity[x, -2, 0]

        cdef int y
        for y in range(self.height):
            self.velocity[0, y, 1] = self.velocity[1, y, 1]
            self.velocity[-1, y, 1] = self.velocity[-2, y, 1]

    cdef float avgVelocityX(self, int x, int y):
        return (self.velocity[x, y - 1, 0] + self.velocity[x, y, 0]
              + self.velocity[x + 1, y - 1, 0] + self.velocity[x + 1, y, 0]) / 4.0

    cdef float avgVelocityY(self, int x, int y):
        return (self.velocity[x - 1, y, 1] + self.velocity[x, y, 1]
              + self.velocity[x - 1, y + 1, 1] + self.velocity[x, y + 1, 1]) / 4.0

    cdef advectVelocity(self, float dt):
        newVelocity = self.velocity.copy()

        cdef float damping = 0.95

        cdef int x, y
        for y in range(1, self.height):
            for x in range(1, self.width):
                if self.space[x, y] and self.space[x - 1, y] and y < self.height - 1:
                    nx = x - dt * self.velocity[x, y, 0]
                    ny = (y + 0.5) - dt * self.avgVelocityY(x, y)
                    newVelocity[x, y, 0] = self.sampleField(nx, ny, VELOCITY_X) * damping

                if self.space[x, y] and self.space[x, y - 1] and x < self.width - 1:
                    nx = (x + 0.5) - dt * self.avgVelocityX(x, y)
                    ny = y - dt * self.velocity[x, y, 1]
                    newVelocity[x, y, 1] = self.sampleField(nx, ny, VELOCITY_Y) * damping

        self.velocity = newVelocity

    cdef advectSmoke(self, float dt):
        newSmoke = self.smoke.copy()

        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.space[x, y] == 0:
                    continue

                u = self.velocity[x, y, 0] + self.velocity[x + 1, y, 0] * 0.5
                v = self.velocity[x, y, 1] + self.velocity[x, y + 1, 1] * 0.5
                x_ = x + 0.5 - dt * u
                y_ = y + 0.5 - dt * v

                newSmoke[x, y] = self.sampleField(x_, y_, SMOKE)

        self.smoke = newSmoke

    def simulate(self, dt):
        stepsPerSecond = 100

        steps = int((dt + self.remainingTime) * stepsPerSecond)
        self.remainingTime = (dt + self.remainingTime) - steps / stepsPerSecond

        cdef int x, y
        for y in range(self.height):
            for x in range(self.width):
                if self.space[x, y] == 0:
                    if self.velocity[x, y, 0] != 0.0:
                        self.velocity[x, y, 0] = 0.0
                    if self.velocity[x, y, 1] != 0.0:
                        self.velocity[x, y, 1] = 0.0
                    if x + 1 < self.width and self.velocity[x + 1, y, 0] != 0.0:
                        self.velocity[x + 1, y, 0] = 0.0
                    if y + 1 < self.height and self.velocity[x, y + 1, 1] != 0.0:
                        self.velocity[x, y + 1, 1] = 0.0

        for i in range(steps):
            self.solveIncompressibility()
        self.extrapolate()
        self.advectVelocity(dt)
        #self.advectSmoke(dt)

    cdef float sampleField(self, float x, float y, field):
        cdef uint32_t x0, y0

        x = max(1, min(x, self.width - 0.001))
        y = max(1, min(y, self.height - 0.001))

        if field == VELOCITY_X:
            y -= 0.5
        else:
            x -= 0.5

        x0 = <uint32_t>floor(x)
        y0 = <uint32_t>floor(y)
        x1 = min(x0 + 1, self.width - 1)
        y1 = min(y0 + 1, self.height - 1)
        tx = x - x0
        ty = y - y0
        sx = 1.0 - tx
        sy = 1.0 - ty

        return (sx*sy * self.velocity[x0, y0, field] +
                tx*sy * self.velocity[x1, y0, field] +
                tx*ty * self.velocity[x1, y1, field] +
                sx*ty * self.velocity[x0, y1, field])

    cpdef (float, float) sampleVelocity(self, float x, float y):
        cdef uint32_t x0, y0

        x = self.conv_coord(x)
        y = self.conv_coord(y)

        u = self.sampleField(x, y, VELOCITY_X)
        v = self.sampleField(x, y, VELOCITY_Y)

        return (u / self.granularity, v / self.granularity)

    def getStreamLine(self, float x, float y, int maxSegments, float minSpeed):
        cdef float segLen = 0.2
        points = [(x, y, 0)]

        if x >= self.width - 2 or y >= self.height - 2:
            return points

        for n in range(maxSegments):
            v_x, v_y = self.sampleVelocity(x, y)
            v = sqrt(v_x**2 + v_y**2)

            if v < minSpeed or v <= 0.0:
                break

            x += v_x / v * segLen
            y += v_y / v * segLen
            #x += v_x * 0.01
            #y += v_y * 0.01
            if x >= self.width / self.granularity - 2 or y >= self.height / self.granularity - 2:
                break

            points.append((x, y, v))

        return points