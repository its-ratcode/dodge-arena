"""The Game: owns the window and runs the main loop."""

import pygame

from app import config
from app.entities.player import Player
from app.meta import APP_NAME
from app.render.arena import build_arena_background
from app.render.effects import ClickMarker
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
        self.player = Player((config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2))
        self.marker: ClickMarker | None = None
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == config.MOVE_MOUSE_BUTTON:
                self.command_move(event.pos, new_click=True)

    def command_move(self, pos, new_click: bool) -> None:
        """Send the player to ``pos``. A fresh click restarts the marker animation;
        while the button is held, the marker follows the cursor and re-pulses."""
        self.player.move_to(pos)
        if new_click or self.marker is None or not self.marker.alive:
            self.marker = ClickMarker(self.player.destination)
        else:
            self.marker.pos.update(self.player.destination)

    def update(self, dt: float) -> None:
        # Holding the move button keeps updating the destination.
        if pygame.mouse.get_pressed()[config.MOVE_MOUSE_BUTTON - 1]:
            self.command_move(pygame.mouse.get_pos(), new_click=False)
        self.player.update(dt)
        if self.marker:
            self.marker.update(dt)

    def draw(self) -> None:
        self.screen.fill(PALETTE.background)
        self.screen.blit(self.background, (0, 0))
        if self.marker and self.marker.alive:
            self.marker.draw(self.screen)
        self.player.draw(self.screen)
