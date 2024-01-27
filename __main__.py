######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################
import pygame
import os

from Feather import Feather
from bitmapfont import BitmapFont
import time
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

SHOW_DEBUG_INFO = True


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

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=flags,vsync=1)

        self.feather = None
        self.loadGraphics()
        self.loadLevel(self.level_i)

        self.cam_x = 0
        self.cam_y = 0
        self.mouse_pos = (0, 0)

        self.scroll_xdir = 0
        self.scroll_ydir = 0

        self.streamLines = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)

        self.edit_mode = False
        self.edit_tile = '#'
        self.edit_tile_i = 0
        self.edit_draw = False
        self.edit_delete = False

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
        self.updateLevelWind()

        feather_spawn = None
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                if self.level[y][x] == "*":  # look for feather spawn
                    feather_spawn = (x, y)

        if feather_spawn is None:
            print(f"Feather Spawn not defined in level {level_name}")
        else:
            self.feather = Feather(FEATHERS)
            self.feather.pos = self.gridToScreen(*feather_spawn)

    def updateLevelWind(self):
        for y in range(self.lev_h):
            for x in range(self.lev_w):
                if self.level[y][x] == '#':
                    self.fluid.space[x + 1, y + 1] = 0
                    self.fluid.velocity[x + 1, y + 1] = (0.0, 0.0)
                else:
                    self.fluid.space[x + 1, y + 1] = 1

    def saveLevel(self, level_name):
        print('saving level: ' + str(level_name))

        with open(f"levels/{level_name}.lvl", "w") as f:
            for line in self.level:
                f.write(line + '\n')

        self.edit_mode = False

    def showStreamLines(self):
        self.fluid.velocity[3, 3] = (10, 4)

        numSegs = 15

        minSpeed = 0.1

        self.streamLines.fill((0,0,0,0))

        for i in range(0, self.lev_w - 1):
            for j in range(0, self.lev_h - 1):
                x = i + 0.5
                y = j + 0.5

                points = [(x, y)]

                for n in range(numSegs):
                    v_x, v_y = self.fluid.sampleVelocity(x + 1, y + 1)
                    v = math.sqrt(v_x**2 + v_y**2)

                    if v < minSpeed:
                        break

                    segLen = 0.2
                    x += v_x / v * segLen
                    y += v_y / v * segLen
                    x += v_x * 0.01
                    y += v_y * 0.01
                    if x >= self.lev_w or y >= self.lev_h:
                        break

                    points.append((x, y))

                if len(points) > 1:
                    points = [self.gridToScreen(*p) for p in points]
                    pygame.draw.lines(self.streamLines, pygame.Color(255, 255, 255), False, points)

        self.screen.blit(self.streamLines, (0, 0))

    def drawTile(self, tile, x, y):
        t = TILES[tile]

        if type(t) is tuple:
            t = t[0] if int(time.time() * 1000) % 500 < 250 else t[1]
        self.screen.blit(t, self.gridToScreen(x, y))

    def setTile(self, tile, x, y):
        line = self.level[y]
        line = line[:x] + tile + line[x+1:]
        self.level[y] = line

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

    def updateEdit(self):
        if self.edit_draw:
            # set tile in grid
            mx, my = self.screenToGrid(*self.mouse_pos)
            self.setTile(self.edit_tile, mx, my)

            self.updateLevelWind()

        if self.edit_delete:
            # delete / set empty tile in grid
            mx, my = self.screenToGrid(*self.mouse_pos)
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
        self.screen.blit(feather, [self.feather.pos[0] - self.cam_x, self.feather.pos[1] - self.cam_y])

        # show wind
        self.showStreamLines()

        # show help
        if SHOW_DEBUG_INFO:
            pygame.draw.rect(self.screen, (40, 60, 80, 64), (SCR_W / 4, TILE_H, SCR_W / 2, TILE_H * 2.75))

            self.font.drawText(self.screen, 'LEV %02i' % self.level_i, x=1, y=1)
            self.font.drawText(self.screen, '%02ix%02i' % (self.lev_w, self.lev_h), x=1, y=2)
            self.font.centerText(self.screen, 'WASD = SCROLL AROUND', y=5)
            self.font.centerText(self.screen, 'F1/F2 = PREV/NEXT LEVEL', y=7)
            self.font.centerText(self.screen, 'F10 = TOGGLE EDIT MODE', y=9)
            self.font.centerText(self.screen, 'F12 = SHOW/HIDE THIS HELP', y=11)

            if self.edit_mode:
                self.font.centerText(self.screen, 'F9 = SAVE (OVERWRITE)', y=13)

        # show edit cursor
        if self.edit_mode:
            cursor = self.edit_tile
            if self.edit_delete:
                cursor = ' '

            mx, my = self.screenToGrid(*self.mouse_pos)
            self.drawTile(cursor, mx, my)
            if int(time.time() * 1000) % 600 < 300:
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)

            rx, ry = self.gridToScreen(mx, my)
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

                if e.button == 1:       # LEFT mousebutton
                    if self.edit_draw:
                        self.edit_draw = False

                elif e.button == 3:     # RIGHT mousebutton
                    if self.edit_delete:
                        self.edit_delete = False

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:       # LEFT mousebutton
                    self.edit_draw = True
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
        self.feather.update(dt, self.frame_cnt)

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

