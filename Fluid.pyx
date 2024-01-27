# cython: language_level=3

import numpy as np
import math

cimport cython
from libc.stdint cimport int8_t

VELOCITY_X = 0
VELOCITY_Y = 1
SMOKE = 2

cdef class Fluid:
    cdef int width
    cdef int height
    cdef double[:, :, :] velocity
    cdef int8_t[:, :] space
    cdef double[:, :] smoke
    cdef double remainingTime

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.velocity = np.zeros(shape=(width, height, 2))
        self.space = np.ones(shape=(width, height), dtype=np.int8)
        self.smoke = np.zeros(shape=(width, height))
        self.remainingTime = 0.0

    def setSpace(self, x, y, s):
        self.space[x, y] = s

    def setVelocity(self, x, y, v):
        self.velocity[x, y, 0] = v[0]
        self.velocity[x, y, 1] = v[1]

    def solveIncompressibility(self):
        cdef int x, y

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
                self.velocity[x, y, 1] -= self.space[x, y - 1] * p
                self.velocity[x + 1, y, 0] += self.space[x + 1, y] * p
                self.velocity[x, y + 1, 1] += self.space[x, y + 1] * p

    def extrapolate(self):
        for x in range(self.width):
            self.velocity[x, 0, 0] = self.velocity[x, 1, 0]
            self.velocity[x, -1, 0] = self.velocity[x, -2, 0]

        for y in range(self.height):
            self.velocity[0, y, 1] = self.velocity[1, y, 1]
            self.velocity[-1, y, 1] = self.velocity[-2, y, 1]

    def avgVelocity(self, _x, _y):
        cdef int x = _x
        cdef int y = _y

        vx = (self.velocity[x - 1, y - 1, 0] + self.velocity[x, y - 1, 0]
            + self.velocity[x - 1, y, 0] + self.velocity[x, y, 0]) / 4.0

        vy = (self.velocity[x - 1, y - 1, 1] + self.velocity[x, y - 1, 1]
            + self.velocity[x - 1, y, 1] + self.velocity[x, y, 1]) / 4.0

        return vx, vy

    def advectVelocity(self, dt):
        newVelocity = self.velocity.copy()

        for y in range(1, self.height):
            for x in range(1, self.width):
                if self.space[x, y] and self.space[x - 1, y] and y < self.height - 1:
                    nx = x - dt * self.velocity[x, y, 0]
                    ny = y - dt * self.avgVelocity(x, y)[1]
                    newVelocity[x, y, 0] = self.sampleField(nx, ny, VELOCITY_X)

                if self.space[x, y] and self.space[x, y - 1] and x < self.width - 1:
                    nx = x - dt * self.avgVelocity(x, y)[0]
                    ny = y - dt * self.velocity[x, y, 1]
                    newVelocity[x, y, 1] = self.sampleField(nx, ny, VELOCITY_Y)

        self.velocity = newVelocity

    def advectSmoke(self, dt):
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

        for y in range(self.height):
            for x in range(self.width):
                if self.space[x, y] == 0 and (self.velocity[x, y, 0] != 0.0 or self.velocity[x, y, 1] != 0.0):
                    print('error', x, y, self.velocity[x, y, 0], self.velocity[x, y, 1])

        for i in range(steps):
            self.solveIncompressibility()
        self.extrapolate()
        self.advectVelocity(dt)
        #self.advectSmoke(dt)

    def sampleField(self, x, y, field):
        x -= 0.5
        y -= 0.5

        x = max(0, min(x, self.width - 0.001))
        y = max(0, min(y, self.height - 0.001))

        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1
        tx = x - x0
        ty = y - y0
        sx = 1.0 - tx
        sy = 1.0 - ty

        if field == VELOCITY_X:
            return (sx*sy * self.velocity[x0, y0, 0] +
                    tx*sy * self.velocity[x1, y0, 0] +
                    tx*ty * self.velocity[x1, y1, 0] +
                    sx*ty * self.velocity[x0, y1, 0])
        elif field == VELOCITY_Y:
            return (sx*sy * self.velocity[x0, y0, 1] +
                    tx*sy * self.velocity[x1, y0, 1] +
                    tx*ty * self.velocity[x1, y1, 1] +
                    sx*ty * self.velocity[x0, y1, 1])

    def sampleVelocity(self, x, y):
        x -= 0.5
        y -= 0.5

        x = max(0, min(x, self.width - 0.001))
        y = max(0, min(y, self.height - 0.001))

        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1
        tx = x - x0
        ty = y - y0
        sx = 1.0 - tx
        sy = 1.0 - ty

        u = (sx*sy * self.velocity[x0, y0, 0]
            + tx*sy * self.velocity[x1, y0, 0]
            + tx*ty * self.velocity[x1, y1, 0]
            + sx*ty * self.velocity[x0, y1, 0]);

        v = (sx*sy * self.velocity[x0, y0, 1]
            + tx*sy * self.velocity[x1, y0, 1]
            + tx*ty * self.velocity[x1, y1, 1]
            + sx*ty * self.velocity[x0, y1, 1]);

        return (u, v)
