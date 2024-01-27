######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################
import pygame
import os

import cam
from Feather import Feather
from Cloud import Cloud
from bitmapfont import BitmapFont
import time
from Fluid import Fluid
import math

from cam import *

try:
    from settings import *
except ImportError:
    FULLSCREEN = False


TILES = {}
FEATHERS = []
CLOUDS = []


SHOW_DEBUG_INFO = True
SHOW_STREAMLINES = True


class Application:
    def __init__(self):
        pygame.init()

        self.cam = cam.Cam()
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

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=flags,vsync=1)
        pygame.mouse.set_visible(False)

        self.feather = None
        self.cloud = None

        self.loadGraphics()
        self.loadLevel(self.level_i)

        self.mouse_pos = (0, 0)

        self.scroll_xdir = 0
        self.scroll_ydir = 0

        self.streamLines = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)

        self.edit_mode = False
        self.edit_tile = '#'
        self.edit_tile_i = 0
        self.edit_draw = False
        self.edit_delete = False

        self.helpScreen = pygame.Surface((SCR_W / 3, 12 * 8), pygame.SRCALPHA)

        self.debugTilePos = None

    def loadGraphics(self):
        TILES['#'] = pygame.image.load('gfx/tile_wall.png')
        TILES[' '] = pygame.image.load('gfx/tile_air.png')
        TILES['*'] = pygame.image.load('gfx/tile_air.png') # feather spawn point, render as empty tile
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
        TILES['d'] = pygame.image.load('gfx/tile_pipe_d.png')
        TILES['b'] = pygame.image.load('gfx/tile_pipe_b.png')
        TILES['q'] = pygame.image.load('gfx/tile_pipe_q.png')
        TILES['p'] = pygame.image.load('gfx/tile_pipe_p.png')
        TILES['-'] = pygame.image.load('gfx/tile_pipe_-.png')
        TILES['l'] = pygame.image.load('gfx/tile_pipe_l.png')
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

        global CLOUDS
        CLOUDS += [pygame.image.load('gfx/cloud1.png'),
                   pygame.image.load('gfx/cloud2.png'),
                   pygame.image.load('gfx/cloud3.png'),
                   pygame.image.load('gfx/cloud4.png'),
                   pygame.image.load('gfx/cloud5.png'),
                   pygame.image.load('gfx/cloud6.png'),
                   pygame.image.load('gfx/cloud7.png'),
                   ]

        self.font = BitmapFont('gfx/heimatfont.png', font_w=8, font_h=8, line_h=10, scr_w=SCR_W, scr_h=SCR_H)

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
        self.cam.reset()

        self.fluid = Fluid(self.lev_w + 2, self.lev_h + 2)
        self.smoke = pygame.Surface((TILE_W * self.lev_w, TILE_H * self.lev_h), pygame.SRCALPHA)
        self.updateLevelWind()

        feather_spawn = None
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                if self.level[y][x] == "*":  # look for feather spawn
                    feather_spawn = (x, y)

        if feather_spawn is None:
            print(f"Feather Spawn not defined in level {level_name}")
        else:
            self.feather = Feather(FEATHERS, self.cam)
            self.feather.pos = self.cam.gridToScreen(*feather_spawn)

        self.cloud = Cloud(CLOUDS)

    def updateLevelWind(self):
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                if self.level[y][x] == '#':
                    self.fluid.setSpace(x + 1, y + 1, 0)
                    self.fluid.setVelocity(x + 1, y + 1, (0.0, 0.0))
                else:
                    self.fluid.setSpace(x + 1, y + 1, 1)

    def saveLevel(self, level_name):
        print('saving level: ' + str(level_name))

        with open(f"levels/{level_name}.lvl", "w") as f:
            for line in self.level:
                f.write(line + '\n')

        self.edit_mode = False

    def showSmoke(self):
        smoke = np.repeat(np.repeat(
            (self.fluid.smoke * 255).astype(np.uint8)[1:-1, 1:-1],
            TILE_W, axis=0), TILE_H, axis=1
        )

        surface_alpha = np.array(self.smoke.get_view('A'), copy=False)
        surface_alpha[:,:] = smoke
        surface_alpha = None

        self.screen.blit(self.smoke, (0, 0))

    def showStreamLines(self):
        numSegs = 15

        minSpeed = 0.1

        self.streamLines.fill((0,0,0,0))

        for i in range(0, self.lev_w - 1):
            for j in range(0, self.lev_h - 1):
                x = i + 0.5
                y = j + 0.5

                points = []
                for (x_, y_) in self.fluid.getStreamLine(x + 1, y + 1, 15, 0.1):
                    x_ = x_ - 1
                    y_ = y_ - 1

                    if x_ >= self.lev_w or y_ >= self.lev_h:
                        continue

                    # todo filter points in wall
                    points.append((x_, y_))

                if len(points) > 1:
                    points = [self.cam.gridToScreen(*p) for p in points]
                    pygame.draw.lines(self.streamLines, pygame.Color(255, 255, 255), False, points)

        self.screen.blit(self.streamLines, (0, 0))

    def drawTile(self, tile, x, y):
        t = TILES[tile]

        if type(t) is tuple:
            t = t[0] if int(time.time() * 1000) % 500 < 250 else t[1]
        self.screen.blit(t, self.cam.gridToScreen(x, y))

    def setTile(self, tile, x, y):
        line = self.level[y]
        line = line[:x] + tile + line[x+1:]
        self.level[y] = line

    def updateCamera(self):
        bounds = (self.lev_w, self.lev_h)
        self.cam.scroll(bounds, (self.scroll_xdir, self.scroll_ydir))

    def updateEdit(self):
        if self.edit_draw:
            # set tile in grid
            mx, my = self.cam.screenToGrid(*self.mouse_pos)
            self.setTile(self.edit_tile, mx, my)

            self.updateLevelWind()

        if self.edit_delete:
            # delete / set empty tile in grid
            mx, my = self.cam.screenToGrid(*self.mouse_pos)
            self.setTile(' ', mx, my)

            self.updateLevelWind()

    def render(self):
        self.screen.fill((40, 60, 80))

        # render level
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                tile = self.level[y][x]

                if tile in TILES:
                    self.drawTile(tile, x, y)

        # render feather
        feather = self.feather.getRender()
        self.screen.blit(feather, [self.feather.pos[0] - self.cam.pos_x, self.feather.pos[1] - self.cam.pos_y])

        # show wind
        if SHOW_STREAMLINES:
            #self.fluid.setVelocity(3, 3, (10, 4))
            #self.fluid.smoke[3, 3] = 1.0
            self.showStreamLines()
            #self.showSmoke()

        # render cloud (player)
        if not self.edit_mode:
            cloud = self.cloud.getRender()
            cx, cy = self.mouse_pos
            self.screen.blit(cloud, (cx, cy))

        # show help
        if SHOW_DEBUG_INFO:
            #pygame.draw.rect(self.helpScreen, (40, 60, 80, 64), (SCR_W / 4, TILE_H, SCR_W / 2, TILE_H * 2.75))
            self.helpScreen.fill((00, 0, 0, 64))

            self.font.drawText(self.helpScreen, 'LEVEL %02i (%02ix%02i)' % (self.level_i, self.lev_w, self.lev_h), x=1, y=1)
            self.font.drawText(self.helpScreen, '')
            self.font.drawText(self.helpScreen, 'WASD = SCROLL AROUND')
            self.font.drawText(self.helpScreen, 'F1/F2 = PREV/NEXT LEVEL')
            self.font.drawText(self.helpScreen, 'F8 = SHOW/HIDE WIND LINES')
            self.font.drawText(self.helpScreen, 'F10 = TOGGLE EDIT MODE')
            self.font.drawText(self.helpScreen, 'F12 = SHOW/HIDE THIS HELP')
            self.font.drawText(self.helpScreen, '')

            if self.edit_mode:
                self.font.drawText(self.helpScreen, '--- EDIT MODE -----------')
                self.font.drawText(self.helpScreen, 'F9 = SAVE (OVERWRITE)')

            self.screen.blit(self.helpScreen, (SCR_W * 0.6, 8))

            # show debug tile
            if self.debugTilePos:
                rx, ry = self.cam.gridToScreen(*self.debugTilePos)
                pygame.draw.rect(self.screen, (255, 255, 0), (rx, ry, TILE_W, TILE_H), width=1)

        # show edit cursor
        if self.edit_mode:
            cursor = self.edit_tile
            if self.edit_delete:
                cursor = ' '

            mx, my = self.cam.screenToGrid(*self.mouse_pos)
            self.drawTile(cursor, mx, my)
            if int(time.time() * 1000) % 600 < 300:
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)

            rx, ry = self.cam.gridToScreen(mx, my)
            pygame.draw.rect(self.screen, color, (rx, ry, TILE_W, TILE_H), width=1)

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
                elif e.key == pygame.K_F12:
                    global SHOW_DEBUG_INFO
                    SHOW_DEBUG_INFO = not SHOW_DEBUG_INFO
                elif e.key == pygame.K_F10:
                    self.edit_mode = not self.edit_mode
                elif e.key == pygame.K_F9:
                    if self.edit_mode:
                        self.saveLevel(self.level_i)

                        # quick and dirty flash
                        self.screen.fill((255, 255, 255))
                        pygame.display.flip()
                        time.sleep(0.2)

                elif e.key == pygame.K_F8:
                    global SHOW_STREAMLINES
                    SHOW_STREAMLINES = not SHOW_STREAMLINES

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
                if e.button == 1:       # LEFT mousebutton
                    if self.edit_mode:
                        if self.edit_draw:
                            self.edit_draw = False

                    else:
                        self.cloud.stopBlowing(self.frame_cnt)

                elif e.button == 3:     # RIGHT mousebutton
                    if self.edit_delete:
                        self.edit_delete = False

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:       # LEFT mousebutton
                    if self.edit_mode:
                        self.edit_draw = True
                    else:
                        self.cloud.startBlowing(self.frame_cnt)

                elif e.button == 3:     # RIGHT mousebutton
                    self.edit_delete = True

            elif e.type == pygame.MOUSEWHEEL:
                direction = ((e.x + e.y) * -1)
                self.edit_tile_i += direction
                self.edit_tile_i %= len(TILES)
                self.edit_tile = list(TILES.keys())[self.edit_tile_i]

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
        self.fluid.simulate(dt)
        self.updateCamera()
        self.feather.update(dt, self.frame_cnt, self.fluid)
        self.cloud.update(dt, self.frame_cnt)

        if self.cloud.isBlowing():
            cx, cy = self.cam.screenToGrid(self.mouse_pos[0] + TILE_W * 0.5, self.mouse_pos[1] + TILE_H * 0.5)
            self.fluid.setVelocity(cx +1, cy +1, (-4, 0))

            self.debugTilePos = (cx, cy)
        else:
            self.debugTilePos = None

        if self.edit_mode:
            self.updateEdit()

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
