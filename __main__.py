######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################

import pygame
import os
from bitmapfont import BitmapFont
import numpy as np

try:
    from settings import *
except ImportError:
    FULLSCREEN = False
    SCALED = False


SCR_W, SCR_H = 640, 360

TILES = {}

TILE_W = 32
TILE_H = 32
SCROLL_SPEED = 4


class Application:
    def __init__(self):
        pygame.init()

        self.running = False

        self.screen = pygame.display.set_mode((SCR_W, SCR_H),
                                              flags=pygame.FULLSCREEN | pygame.SCALED)
        self.level_i = 1
        self.level = []
        self.lev_w = 0
        self.lev_h = 0
        self.level_amount = len(os.listdir("./levels"))
        flags = 0

        if FULLSCREEN:
            if SCALED:
                flags = pygame.FULLSCREEN | pygame.SCALED
            # no fullscreen if not SCALED
        else:
            if SCALED:
                flags = pygame.SCALED

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=flags)

        self.loadGraphics()
        self.loadLevel(self.level_i)

        self.cam_x = 0
        self.cam_y = 0

        self.scroll_xdir = 0
        self.scroll_ydir = 0

    def loadGraphics(self):
        TILES['#'] = pygame.image.load('gfx/tile_wall.png')
        TILES['F'] = pygame.image.load('gfx/tile_feet.png')

        self.font = BitmapFont('gfx/heimatfont.png', font_w=8, font_h=8, scr_w=SCR_W, scr_h=SCR_H)

    def loadLevel(self, level_name):
        print('loading level: ' + str(level_name))
        with open("levels/{}.lvl".format(level_name)) as f:
            self.level = [line.strip() for line in f.readlines()]   # note: levels should always contain a border!
        self.lev_w = len(self.level[0])
        self.lev_h = len(self.level)

        self.velocity = np.zeros(shape=(self.lev_w, self.lev_h, 2))
        self.space = np.zeros(shape=(self.lev_w, self.lev_h))

        for y in range(self.lev_h):
            for x in range(self.lev_w):
                self.space[x, y] = 0.0 if self.level[y][x] == '#' else 1.0

    def drawTile(self, tile, x, y):
        self.screen.blit(TILES[tile], (x * TILE_W - self.cam_x, y * TILE_H - self.cam_y))

    def updateCamera(self):
        self.cam_x += self.scroll_xdir * SCROLL_SPEED
        self.cam_y += self.scroll_ydir * SCROLL_SPEED

        if self.cam_x < 0:
            self.cam_x = 0
        if self.cam_x > self.lev_w * TILE_W - SCR_W:
            self.cam_x = self.lev_w * TILE_W - SCR_W
        if self.cam_y < 0:
            self.cam_y = 0
        if self.cam_y > self.lev_h * TILE_H - SCR_H:
            self.cam_y = self.lev_h * TILE_H - SCR_H

    def render(self):
        self.screen.fill((40, 60, 80))

        # render level
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                tile = self.level[y][x]

                if tile in TILES:
                    self.drawTile(tile, x, y)

        self.font.centerText(self.screen, 'WASD = SCROLL AROUND', y=5)
        self.font.centerText(self.screen, 'F1/F2 = PREV/NEXT LEVEL', y=7)
        self.font.drawText(self.screen, 'LEV %02i' % self.level_i, x=1, y=1)

        pygame.display.flip()

    def controls(self):
        events = pygame.event.get()
        modstate = pygame.key.get_mods()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif e.key == pygame.K_F1:
                    self.level_i -= 1
                    if self.level_i < 1:
                        self.level_i = self.level_amount
                    self.loadLevel(self.level_i)
                elif e.key == pygame.K_F2:
                    self.level_i += 1
                    if self.level_i > self.level_amount:
                        self.level_i = 1
                    self.loadLevel(self.level_i)

                elif e.key == pygame.K_RETURN:
                    if modstate & pygame.KMOD_ALT:
                        pygame.display.toggle_fullscreen()

                elif e.key == pygame.K_w:
                    self.scroll_ydir = -1
                elif e.key == pygame.K_s:
                    self.scroll_ydir = 1
                elif e.key == pygame.K_a:
                    self.scroll_xdir = -1
                elif e.key == pygame.K_d:
                    self.scroll_xdir = 1

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_w:
                    if self.scroll_ydir < 0:
                        self.scroll_ydir = 0
                elif e.key == pygame.K_s:
                    if self.scroll_ydir > 0 :
                        self.scroll_ydir = 0
                elif e.key == pygame.K_a:
                    if self.scroll_xdir < 0:
                        self.scroll_xdir = 0
                elif e.key == pygame.K_d:
                    if self.scroll_xdir > 0:
                        self.scroll_xdir = 0

            elif e.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.updateCamera()

    def run(self):
        self.running = True

        clock = pygame.time.Clock()

        while self.running:
            self.render()
            self.controls()
            self.update()

            clock.tick(60)

        pygame.quit()


app = Application()
app.run()

