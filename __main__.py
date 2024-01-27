######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################

import pygame
import os
from bitmapfont import BitmapFont
import time
import random
from Fluid import Fluid
import math

try:
    from settings import *
except ImportError:
    FULLSCREEN = False


SCR_W, SCR_H = 640, 360

TILES = {}
FEATHERS = []

TILE_W = 32
TILE_H = 32
SCROLL_SPEED = 4

class Application:
    def __init__(self):
        pygame.init()

        self.running = False
        self.frame_cnt = 0

        self.level_i = 1
        self.level = []
        self.lev_w = 0
        self.lev_h = 0
        self.level_amount = len(os.listdir("./levels"))

        flags = pygame.SCALED

        if FULLSCREEN:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=flags)

        self.loadGraphics()
        self.loadLevel(self.level_i)

        self.cam_x = 0
        self.cam_y = 0
        self.mouse_pos = (0, 0)

        self.scroll_xdir = 0
        self.scroll_ydir = 0

        self.feather_anim_cnt = 0
        self.feather_anim_dir = 1
        self.feather_anim_speed = 8     # lower means faster
        self.feather_anim_rot = 0
        self.feather_anim_rot_dir = 2

        self.streamLines = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)

    def loadGraphics(self):
        TILES['#'] = pygame.image.load('gfx/tile_wall.png')
        TILES[' '] = pygame.image.load('gfx/tile_air.png')
        TILES['/'] = pygame.image.load('gfx/tile_air__rain.png')
        TILES['F'] = (pygame.image.load('gfx/tile_feet.png'), pygame.image.load('gfx/tile_feet2.png'))
        TILES['l'] = pygame.image.load('gfx/tile_lantern.png')
        TILES['L'] = pygame.image.load('gfx/tile_lanterntop.png')
        TILES['_'] = pygame.image.load('gfx/tile_floor.png')
        TILES['g'] = pygame.image.load('gfx/tile_grill.png')
        TILES['T'] = pygame.image.load('gfx/tile_housetop_antenna.png')
        TILES['c'] = pygame.image.load('gfx/tile_air__AC_l.png')
        TILES['C'] = pygame.image.load('gfx/tile_air__AC_r.png')
        TILES['h'] = pygame.image.load('gfx/tile_house_l.png')
        TILES['i'] = pygame.image.load('gfx/tile_house_m.png')
        TILES['j'] = pygame.image.load('gfx/tile_house_r.png')
        TILES['H'] = pygame.image.load('gfx/tile_housetop_l.png')
        # TILES['I'] = pygame.image.load('gfx/tile_housetop_m.png')
        # TILES['J'] = pygame.image.load('gfx/tile_housetop_r.png')

        global FEATHERS
        FEATHERS += [pygame.image.load('gfx/feather1.png'),
                     pygame.image.load('gfx/feather2.png'),
                     pygame.image.load('gfx/feather3.png'),
                     pygame.image.load('gfx/feather4.png'),
                     pygame.image.load('gfx/feather5.png'),
                     pygame.image.load('gfx/feather6.png'),
                     pygame.image.load('gfx/feather7.png'),
                     pygame.image.load('gfx/feather8.png'),
                     ]

        self.font = BitmapFont('gfx/heimatfont.png', font_w=8, font_h=8, scr_w=SCR_W, scr_h=SCR_H)

    def loadLevel(self, level_name):
        print('loading level: ' + str(level_name))

        with open(f"levels/{level_name}.lvl") as f:
            self.level = [line.rstrip("\r\n") for line in f.readlines()]

        # find longest line
        lev_w = 0
        for line in self.level:
            lev_w = max(lev_w, len(line))

        # pad shorter lines with spaces
        for i, line in enumerate(self.level):
            if len(line) < lev_w:
                self.level[i] += ' ' * (lev_w - len(line))

        self.lev_w = lev_w
        self.lev_h = len(self.level)
        self.cam_x = 0
        self.cam_y = 0

        self.fluid = Fluid(self.lev_w + 2, self.lev_h + 2)

        for y in range(self.lev_h):
            for x in range(self.lev_w):
                self.fluid.space[x + 1, y + 1] = 0 if self.level[y][x] == '#' else 1

    def showStreamLines(self):
        numSegs = 15

        minSpeed = 0.1

        for i in range(0, self.lev_w - 1):
            for j in range(0, self.lev_h - 1):
                x = (i + 0.5) * TILE_W
                y = (j + 0.5) * TILE_H

                points = [(x, y)]

                for n in range(numSegs):
                    v_x, v_y = self.fluid.sampleVelocity(x / TILE_W, y / TILE_H)
                    v = math.sqrt(v_x**2 + v_y**2)

                    if v < minSpeed:
                        break

                    #segLen = 0.2
                    #x += v_x / v * segLen
                    #y += v_y / v * segLen
                    x += v_x * 0.01
                    y += v_y * 0.01
                    if x > SCR_W or y > SCR_H:
                        break

                    points.append((x, y))

                if len(points) > 1:
                    pygame.draw.lines(self.streamLines, pygame.Color(255, 255, 255), False, points)

        self.screen.blit(self.streamLines, (0, 0))

    def drawTile(self, tile, x, y):
        t = TILES[tile]

        if type(t) is tuple:
            t = t[0] if int(time.time() * 1000) % 500 < 250 else t[1]
        self.screen.blit(t, self.gridToScreen(x, y))

    def gridToScreen(self, x, y):
        return x * TILE_W - self.cam_x, y * TILE_H - self.cam_y

    def screenToGrid(self, x, y):
        return (x + self.cam_x) // TILE_W, (y + self.cam_y) // TILE_H

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

    def updateFeather(self):
        if self.frame_cnt % self.feather_anim_speed == 0:
            self.feather_anim_cnt += self.feather_anim_dir

            self.feather_anim_cnt %= 8

            if int(random.random() * 8) == 0:
                self.feather_anim_dir *= -1

        self.feather_anim_rot += self.feather_anim_rot_dir
        self.feather_anim_rot %= 360

        if int(random.random() * 60) == 0:
            self.feather_anim_rot_dir *= -1

    def render(self):
        self.screen.fill((40, 60, 80))

        # render level
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                tile = self.level[y][x]

                if tile in TILES:
                    self.drawTile(tile, x, y)

        # render feather
        feather = FEATHERS[self.feather_anim_cnt]
        feather = pygame.transform.rotate(feather, self.feather_anim_rot)
        self.screen.blit(feather, (128 - (feather.get_width() - TILE_W) / 2, 64 - (feather.get_height() - TILE_H) / 2))

        self.font.drawText(self.screen, 'LEV %02i' % self.level_i, x=1, y=1)
        self.font.drawText(self.screen, '%02ix%02i' % (self.lev_w, self.lev_h), x=1, y=2)
        self.font.centerText(self.screen, 'WASD = SCROLL AROUND', y=5)
        self.font.centerText(self.screen, 'F1/F2 = PREV/NEXT LEVEL', y=7)

        self.showStreamLines()

        pygame.display.flip()

    def controls(self):
        events = pygame.event.get()
        modstate = pygame.key.get_mods()
        self.mouse_pos = pygame.mouse.get_pos()

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

            elif e.type == pygame.MOUSEBUTTONUP:
                # TODO do relevant things on mouse click
                print(f"clicked on grid position: {self.screenToGrid(*self.mouse_pos)}")

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

    def update(self, dt):
        # self.fluid.simulate(dt)
        self.updateCamera()
        self.updateFeather()

    def run(self):
        self.running = True

        clock = pygame.time.Clock()
        dt = 0

        while self.running:
            t = time.time()

            self.render()
            self.controls()
            self.update(dt)

            clock.tick(60)
            self.frame_cnt += 1
            dt = time.time() - t

        pygame.quit()


app = Application()
app.run()

