"""The Game: owns the window, the main loop and the current run."""

import pygame

from app import config
from app.core.world import World
from app.meta import APP_NAME
from app.render.arena import build_arena_background
from app.render.text import draw_text
from app.theme.palette import PALETTE


class Game:
    """Creates the window and runs a frame-rate independent main loop.

    Each frame: handle input -> update the simulation by ``dt`` seconds -> draw.
    A run lives in a ``World``; restarting just creates a new one.
    """

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        self.clock = pygame.time.Clock()
        self.background = build_arena_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))
        self.world = World()
        self.running = True

    # --- Main loop ----------------------------------------------------------------------
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.world.over:
                    self.world = World()                      # restart
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == config.MOVE_MOUSE_BUTTON:
                if not self.world.over:
                    self.world.command_move(event.pos, new_click=True)

    def update(self, dt: float) -> None:
        # Holding the move button keeps updating the destination.
        if not self.world.over and pygame.mouse.get_pressed()[config.MOVE_MOUSE_BUTTON - 1]:
            self.world.command_move(pygame.mouse.get_pos(), new_click=False)
        self.world.update(dt)

    # --- Drawing ------------------------------------------------------------------------
    def draw(self) -> None:
        self.screen.fill(PALETTE.background)
        self.screen.blit(self.background, (0, 0))
        self.world.draw(self.screen)
        draw_text(self.screen, f"{self.world.survival_time:0.1f}s", 32, PALETTE.text, bold=True,
                  midtop=(config.SCREEN_WIDTH // 2, 14))
        if self.world.over:
            self.draw_game_over()

    def draw_game_over(self) -> None:
        self.screen.blit(self.overlay, (0, 0))
        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        draw_text(self.screen, "GAME OVER", 64, PALETTE.danger, bold=True, center=(cx, cy - 70))
        draw_text(self.screen, f"You survived {self.world.survival_time:0.2f} seconds", 26, PALETTE.text,
                  center=(cx, cy))
        draw_text(self.screen, "Press R to restart   |   Esc to quit", 22, PALETTE.text_dim,
                  center=(cx, cy + 60))
