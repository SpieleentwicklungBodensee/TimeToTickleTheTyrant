import numpy as np

class Fluid:
    def __init__(self, numX, numY):
        self.velocity = np.zeros(shape=(numX, numY, 2))
        self.space = np.zeros(shape=(numX, numY))