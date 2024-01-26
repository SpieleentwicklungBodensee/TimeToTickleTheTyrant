import pygame

SCR_W, SCR_H = 640, 360


class Application():
    def __init__(self):
        pygame.init()

        self.running = False

        self.screen = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.FULLSCREEN|pygame.SCALED)

    def render(self):
        self.screen.fill((255, 0, 0))

        pygame.display.flip()

    def controls(self):
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

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

