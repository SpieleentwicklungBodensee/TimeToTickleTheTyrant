import numpy as np
import math

GRAVITY = np.array([0., 20.])
DRAG = .0005


class Feather:
    def __init__(self):
        self.v = np.array([0., 0.])
        self.pos = np.array([0., 0.])

    def update(self, dt):
        self.pos += self.v * dt

        self.v += (dt * GRAVITY)
        drag_scalar = np.dot(self.v, self.v) * DRAG
        v_norm = self.v / (np.linalg.norm(self.v) + 1e-16)
        drag_v_norm = np.array([element * -1 for element in v_norm])
        drag_v = drag_v_norm * drag_scalar
        self.v += drag_v


def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))
