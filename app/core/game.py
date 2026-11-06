"""The Game: owns the window and runs the main loop."""

import pygame

from app import config
from app.meta import APP_NAME
from app.render.arena import build_arena_background
from app.theme.palette import PALETTE


class Game:
    """Creates the window and runs a frame-rate independent main loop.

    Each frame: handle input -> update the simulation by ``dt`` seconds -> draw.
    """

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        self.clock = pygame.time.Clock()
        self.background = build_arena_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.running = True

    def run(self) -> None:
        while self.running:
            # Clamp dt so a stall (e.g. dragging the window) can't make things jump.
            dt = min(self.clock.tick(config.FPS) / 1000.0, config.MAX_FRAME_DT)
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds (nothing to simulate yet)."""

    def draw(self) -> None:
        self.screen.fill(PALETTE.background)
        self.screen.blit(self.background, (0, 0))
