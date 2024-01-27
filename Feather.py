import numpy as np
import random
import pygame


GRAVITY = np.array([0., 16.])
DRAG = .0005
FEATHER_SPRITE_SIZE = 32


class Feather:
    def __init__(self, feather_sprites, cam, level):
        self.cam = cam
        self.level = level
        self.feather_sprites = feather_sprites
        self.v = np.array([0., 0.])
        self.pos = np.array([0., 0.])
        self.anim_cnt = 0
        self.anim_dir = 1
        self.anim_speed = 8     # lower means faster
        self.anim_rot = 0
        self.anim_rot_dir = 2

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

        # x, y = self.cam.screenToGrid(self.pos[0], self.pos[1])
        # v_wind = fluid.sampleVelocity(x + 1, y + 1)  # +1 for fluid grid offset
        # print(v_wind)
        # a_wind = np.array(v_wind) * DRAG
        #
        # self.v += a_wind

        drag_scalar = np.dot(self.v, self.v) * DRAG
        v_norm = self.v / (np.linalg.norm(self.v) + 1e-16)
        drag_v_norm = np.array([element * -1 for element in v_norm])
        drag_v = drag_v_norm * drag_scalar
        self.v += drag_v

    def updatePosition(self, dt):
        potential_pos = self.pos + self.v * dt
        if self.isInWall(potential_pos):
            # pot_x,pot_y = self.cam.worldToGrid(potential_pos[0], potential_pos[1])
            # x,y = self.cam.worldToGrid(self.pos[0], self.pos[1])
            # print(f"Xdiff: {x - pot_x}   -   Ydiff: {y-pot_y}")
            pass
        else:
            self.pos = potential_pos

    def getRender(self):
        feather = self.feather_sprites[self.anim_cnt]
        feather = pygame.transform.rotate(feather, self.anim_rot)
        return feather

    def getRenderPos(self):
        return [self.pos[0] - self.cam.pos_x - FEATHER_SPRITE_SIZE / 2,
                self.pos[1] - self.cam.pos_y - FEATHER_SPRITE_SIZE / 2]

    def isInWall(self, potential_pos):
        x,y = self.cam.worldToGrid(potential_pos[0], potential_pos[1])
        tile = self.level[y][x]
        return tile == "#"
