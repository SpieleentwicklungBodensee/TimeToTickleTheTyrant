######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################

import pygame

SCR_W, SCR_H = 640, 360


TILES = {}

TILE_W = 32
TILE_H = 32


LEVEL = ['################################',
         '#                              #',
         '#                              #',
         '#                              #',
         '#     ### ### ### ### ###      #',
         '#      #   #   #   #   #       #',
         '#      #   #   #   #   #       #',
         '#      #   #   #   #   #       #',
         '#                              #',
         '#                              #',
         '#                              #',
         '#                              #',
         '#                              #',
         '#                              #',
         '#                              #',
         '################################',
         ]

LEV_W = len(LEVEL[0])
LEV_H = len(LEVEL)


class Application:
    def __init__(self):
        pygame.init()

        self.running = False

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.FULLSCREEN|pygame.SCALED)

        self.loadGraphics()

        self.cam_x = 0
        self.cam_y = 0

    def loadGraphics(self):
        TILES['#'] = pygame.image.load('gfx/tile_wall.png')

    def drawTile(self, tile, x, y):
        self.screen.blit(TILES[tile], (x * TILE_W - self.cam_x, y * TILE_H - self.cam_y))

    def render(self):
        self.screen.fill((40, 60, 80))

        # render level
        for y in range(LEV_H):
            for x in range(LEV_W):
                tile = LEVEL[y][x]

                if tile in TILES:
                    #self.screen.blit(TILES[tile], (x * TILE_W, y * TILE_H))
                    self.drawTile(tile, x, y)

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

                elif e.key == pygame.K_RETURN:
                    if modstate & pygame.KMOD_ALT:
                        pygame.display.toggle_fullscreen()

            elif e.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.cam_x += 4

        if self.cam_x > LEV_W * TILE_W:
            self.cam_x = -LEV_W * TILE_W

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

