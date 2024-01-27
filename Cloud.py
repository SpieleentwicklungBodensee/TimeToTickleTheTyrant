import numpy as np
import random
import pygame

GRAVITY = np.array([0., 20.])
DRAG = .0005


class Cloud:
    def __init__(self, sprites):
        self.sprites = sprites
        self.v = np.array([0., 0.])
        self.pos = np.array([0., 0.])
        self.anim_cnt = 0
        self.anim_dir = 1
        self.anim_speed = 4     # lower means faster
        self.anim_rot = 0

        self.blowing = False
        self.frame_cnt_offset = 0

    def update(self, dt, frame_cnt):
        self.update_phys(dt)
        self.updateAnimationData(frame_cnt)

    def updateAnimationData(self, frame_cnt):
        if (frame_cnt - self.frame_cnt_offset) % self.anim_speed != 0:
            return

        # cloud animation steps:
        # ----------------------
        # sprite 0 = not animated (idle)
        # sprite 1-4 = initialize blow
        # sprite 5-6 = blow
        # sprite 4 = deinitialize blow

        # idle
        if self.anim_cnt == 0:
            return
        # initialize blow
        elif self.anim_cnt < 4:
            self.anim_cnt += 1
        # initialize or deinitialize blow
        elif self.anim_cnt == 4:
            if self.blowing:
                self.anim_cnt += 1
            else:
                self.anim_cnt = 0
        # blow
        else:
            if self.anim_cnt == 5:
                self.anim_cnt = 6
            else:
                self.anim_cnt = 5

    def update_phys(self, dt):
        self.pos += self.v * dt
        self.v += (dt * GRAVITY)
        drag_scalar = np.dot(self.v, self.v) * DRAG
        v_norm = self.v / (np.linalg.norm(self.v) + 1e-16)
        drag_v_norm = np.array([element * -1 for element in v_norm])
        drag_v = drag_v_norm * drag_scalar
        self.v += drag_v

    def getRender(self):
        sprite = self.sprites[self.anim_cnt]
        sprite = pygame.transform.rotate(sprite, self.anim_rot)
        return sprite

    def startBlowing(self, frame_cnt):
        if self.blowing:
            return

        self.blowing = True
        self.anim_cnt = 1
        self.frame_cnt_offset = frame_cnt-1

    def stopBlowing(self, frame_cnt):
        self.blowing = False
        self.anim_cnt = 4