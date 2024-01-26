######################
###                ###
### TIME TO TICKLE ###
###   THE TYRANT   ###
###                ###
######################

import pygame

SCR_W, SCR_H = 640, 360


TILES = {}

TILE_W = 16
TILE_H = 16


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

    def loadGraphics(self):
        TILES['#'] = pygame.image.load('gfx/tile_wall.png')

    def render(self):
        self.screen.fill((0, 0, 0))

        # render level
        for y in range(LEV_H):
            for x in range(LEV_W):
                tile = LEVEL[y][x]

                if tile in TILES:
                    self.screen.blit(TILES[tile], (x * TILE_W, y * TILE_H))

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

    def update(self):
        pass

    def run(self):
        self.running = True

        while self.running:
            self.render()
            self.controls()
            self.update()

        pygame.quit()


app = Application()
app.run()

