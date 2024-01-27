TILE_W = 32
TILE_H = 32

SCR_W, SCR_H = 640, 360
SCROLL_SPEED = 4

class Cam:
    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0

    def reset(self):
        self.pos_x = 0
        self.pos_y = 0

    def gridToScreen(self, x, y):
        return x * TILE_W - self.pos_x, y * TILE_H - self.pos_y

    def screenToGrid(self,x, y):
        return (x + self.pos_x) // TILE_W, (y + self.pos_y) // TILE_H

    def scroll(self, bounds, scroll_directions):
        self.pos_x += scroll_directions[0] * SCROLL_SPEED
        self.pos_y += scroll_directions[1] * SCROLL_SPEED

        if self.pos_x < 0:
            self.pos_x = 0
        if self.pos_x > bounds[0] * TILE_W - SCR_W:
            self.pos_x = bounds[0] * TILE_W - SCR_W
        if self.pos_y < 0:
            self.pos_y = 0
        if self.pos_y > bounds[1] * TILE_H - SCR_H:
            self.pos_y = bounds[1] * TILE_H - SCR_H
        pass
