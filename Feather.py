import cam

import numpy as np
import random
import pygame


GRAVITY = np.array([0., 16.])
DRAG = .0005
COLLISION_RADIUS = 12 # not an actual radius. Half the collision square's height
COLLISION_TILES = ["#", 'h', 'i', 'j', 'H', 'X', 'Y', 'd', 'b', 'q', 'p', 'l',
                   '-', '+', 'o', 'u', 'n', 'w', 'm', 'c', 'C', '_']


class Feather:
    def __init__(self, feather_sprites, _cam, level):
        self.cam = _cam
        self.level = level
        self.feather_sprites = feather_sprites
        self.v = np.array([0., 0.])
        self.pos = np.array([0., 0.])
        self.anim_cnt = 0
        self.anim_dir = 1
        self.anim_speed = 8     # lower means faster
        self.anim_rot = 0
        self.anim_rot_dir = 2

        self.colllision_radius = COLLISION_RADIUS

    def update(self, dt, frame_cnt, fluid):
        self.update_phys(dt, fluid)
        self.updateAnimationData(frame_cnt)

    def updateAnimationData(self, frame_cnt):
        if frame_cnt % self.anim_speed == 0:
            self.anim_cnt += self.anim_dir

            self.anim_cnt %= 8

            if int(random.random() * 8) == 0:
                self.anim_dir *= -1
        self.anim_rot += self.anim_rot_dir
        self.anim_rot %= 360
        if int(random.random() * 60) == 0:
            self.anim_rot_dir *= -1

    def update_phys(self, dt, fluid):
        self.updatePosition(dt)
        self.v += (dt * GRAVITY)

        x, y = self.pos[0] / cam.TILE_W, self.pos[1] / cam.TILE_H
        v_wind = np.array(fluid.sampleVelocity(x, y))
        dv = self.v - v_wind * 1000.0

        drag_scalar = np.dot(dv, dv) * DRAG
        v_norm = dv / max(np.linalg.norm(dv), 1e-16)
        self.v -= v_norm * drag_scalar

    def updatePosition(self, dt):
        potential_pos = self.pos + self.v * dt

        # NOTE TO FUTURE SELF: ALWAYS CHECK HORIZ/VERT SEPERATELY!!

        # horizontal check
        nbr_wall = self.detectWall((potential_pos[0], self.pos[1]))
        if nbr_wall is not None:
            if nbr_wall[0] != 0: # left/right wall
                self.v[0] = -self.v[0] /10  # fudge v to not get stuck in wall

        # vertical check
        nbr_wall = self.detectWall((self.pos[0], potential_pos[1]))
        if nbr_wall is not None:
            if nbr_wall[1] != 0: # top/bottom wall
                self.v[1] = -self.v[1] /10  # fudge v to not get stuck in wall

        corrected_pos = self.pos + self.v * dt
        self.pos = corrected_pos

    def render(self, screen):
        feather = self.feather_sprites[self.anim_cnt]
        feather = pygame.transform.rotate(feather, self.anim_rot)
        renderpos = (self.pos[0] - self.cam.pos_x - feather.get_width() / 2, self.pos[1] - self.cam.pos_y - feather.get_height() / 2)

        screen.blit(feather, renderpos)

    def getBoundingBox(self, pos=None):
        if pos is None:
            pos = self.pos

        return pos[0] - COLLISION_RADIUS, pos[1] - COLLISION_RADIUS, pos[0] + COLLISION_RADIUS, pos[1] + COLLISION_RADIUS

    def detectWall(self, potential_pos):

        #  0      2
        #   o----o
        #   |    |
        #   |    |
        #   o----o
        #  1      3

        collision_point = np.copy(potential_pos)
        bbox = self.getBoundingBox(collision_point)

        points = [(bbox[0], bbox[1]),
                  (bbox[0], bbox[3]),
                  (bbox[2], bbox[1]),
                  (bbox[2], bbox[3]),
                  ]

        for px, py in points:
            x, y = self.cam.worldToGrid(px, py)
            tile = self.level[y][x]
            if tile in COLLISION_TILES:
                xcoord,ycoord = self.cam.worldToGrid(self.pos[0], self.pos[1])
                return x - xcoord, y - ycoord

        return None
