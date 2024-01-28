TILE_W = 32
TILE_H = 32

SCR_W, SCR_H = 640, 360
SCROLL_SPEED = 4
SCROLL_ACCEL = 0.5
SCROLL_DECEL = 0.25

CAMERA_RADIUS_X = SCR_W / 4
CAMERA_RADIUS_Y = SCR_H / 4

class Cam:
    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0

        self.dir_x = 0
        self.dir_y = 0

    def reset(self):
        self.pos_x = 0
        self.pos_y = 0

    def gridToScreen(self, x, y):
        return int(x * TILE_W - self.pos_x), int(y * TILE_H - self.pos_y)

    def screenToGrid(self,x, y):
        return int((x + self.pos_x) // TILE_W), int((y + self.pos_y) // TILE_H)

    def worldToGrid(self,x, y):
        return int(x // TILE_W), int(y // TILE_H)

    def worldToScreen(self, x, y):
        return int(x - self.pos_x), int(y - self.pos_y)

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

    def followPos(self, x, y):
        if self.pos_x + SCR_W / 2 + CAMERA_RADIUS_X < x:
            self.dir_x += SCROLL_ACCEL
        elif self.pos_x + SCR_W / 2 - CAMERA_RADIUS_X > x:
            self.dir_x -= SCROLL_ACCEL
        else:
            # decelerate
            if self.dir_x >= SCROLL_DECEL:
                self.dir_x -= SCROLL_DECEL
            elif self.dir_x <= -SCROLL_DECEL:
                self.dir_x += SCROLL_DECEL
            else:
                self.dir_x = 0

        if self.pos_y + SCR_H / 2 + CAMERA_RADIUS_Y < y:
            self.dir_y += SCROLL_ACCEL
        elif self.pos_y + SCR_H / 2 - CAMERA_RADIUS_Y > y:
            self.dir_y -= SCROLL_ACCEL
        else:
            # decelerate
            if self.dir_y >= SCROLL_DECEL:
                self.dir_y -= SCROLL_DECEL
            elif self.dir_y <= -SCROLL_DECEL:
                self.dir_y += SCROLL_DECEL
            else:
                self.dir_y = 0

        if self.dir_x > SCROLL_SPEED:
            self.dir_x = SCROLL_SPEED
        elif self.dir_x < -SCROLL_SPEED:
            self.dir_x = -SCROLL_SPEED

        if self.dir_y > SCROLL_SPEED:
            self.dir_y = SCROLL_SPEED
        elif self.dir_y < -SCROLL_SPEED:
            self.dir_y = -SCROLL_SPEED

        self.pos_x += self.dir_x
        self.pos_y += self.dir_y
