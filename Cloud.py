import numpy as np
import random
import pygame
import math

GRAVITY = np.array([0., 20.])
DRAG = .0005


class Cloud:
    def __init__(self, sprites, cam):
        self.sprites = sprites
        self.cam = cam
        self.v = np.array([0., 0.])
        self.pos = np.array([0., 0.])
        self.anim_cnt = 0
        self.anim_dir = 1
        self.anim_speed = 4     # lower means faster
        self.anim_rot = 0

        self.blowing = False
        self.frame_cnt_offset = 0

        self.lookDirection = -1

    def update(self, dt, frame_cnt, feather):
        self.update_phys(dt)
        self.updateAnimationData(frame_cnt)
        self.updateRotation(feather)

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

    def updateRotation(self, feather):
        xdiff = self.pos[0] - feather.pos[0]
        ydiff = self.pos[1] - feather.pos[1]

        if xdiff != 0:
            angle = math.atan(ydiff / xdiff)
            self.anim_rot = -math.degrees(angle)

        if xdiff < 0:
            self.setLookDirection(1)
        else:
            self.setLookDirection(-1)

    def render(self, screen):
        sprite = self.sprites[self.anim_cnt]

        if self.lookDirection > 0:
            sprite = pygame.transform.flip(sprite, True, False)

        sprite = pygame.transform.rotate(sprite, self.anim_rot)
        renderpos = (self.pos[0] - self.cam.pos_x - sprite.get_width() / 2, self.pos[1] - self.cam.pos_y - sprite.get_height() / 2)

        screen.blit(sprite, renderpos)

    def startBlowing(self, frame_cnt):
        if self.blowing:
            return

        self.blowing = True
        self.anim_cnt = 1
        self.frame_cnt_offset = frame_cnt-1

    def stopBlowing(self, frame_cnt):
        self.blowing = False
        self.anim_cnt = 4

    def isBlowing(self):
        if self.anim_cnt > 4:
            return True

        return False

    def getBlowDirection(self):
        a = math.radians(self.anim_rot)
        return (math.cos(a) * self.lookDirection, -math.sin(a) * self.lookDirection)

    def setLookDirection(self, d):
        if d < 0:
            self.lookDirection = -1
        else:
            self.lookDirection = 1

    def getLookDirection(self):
        return self.lookDirection

    def setPosition(self, x, y):
        self.pos = np.array([float(x), float(y)])
