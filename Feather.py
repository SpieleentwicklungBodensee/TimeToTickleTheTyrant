import numpy as np
import random
import pygame


GRAVITY = np.array([0., 1.])
DRAG = .0005


class Feather:
    def __init__(self, feather_sprites, cam):
        self.cam = cam
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
        self.pos += self.v * dt
        self.v += (dt * GRAVITY)

        # x, y = self.cam.screenToGrid(self.pos[0], self.pos[1])
        # v_wind = fluid.sampleVelocity(x, y)
        # print(v_wind)
        # a_wind = np.array(v_wind) * DRAG
        #
        # self.v += a_wind

        drag_scalar = np.dot(self.v, self.v) * DRAG
        v_norm = self.v / max(np.linalg.norm(self.v), 1e-16)
        drag_v_norm = -v_norm
        drag_v = drag_v_norm * drag_scalar
        self.v += drag_v

    def getRender(self):
        feather = self.feather_sprites[self.anim_cnt]
        feather = pygame.transform.rotate(feather, self.anim_rot)
        return feather
