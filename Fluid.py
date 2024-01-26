import numpy as np

class Fluid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.velocity = np.zeros(shape=(width, height, 2))
        self.space = np.zeros(shape=(width, height))

