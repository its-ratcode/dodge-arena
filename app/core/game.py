"""The Game: owns the window, the main loop and the current run."""

import pygame

from app import config
from app.core.storage import SaveFile
from app.core.world import World
from app.entities.laser import Laser
from app.meta import APP_NAME
from app.progression.profile import Profile, RunResult
from app.render.arena import build_arena_background
from app.render.text import draw_text
from app.theme.palette import PALETTE
from app.ui.hud import Hud
from app.util.timefmt import fmt_time


class Game:
    """Creates the window and runs a frame-rate independent main loop.

    Each frame: handle input -> update the simulation by ``dt`` seconds -> draw.
    A run lives in a ``World``; restarting just creates a new one. The
    ``Profile`` (coins, upgrades, best time) outlives runs and is saved when
    each one ends. ``save_path`` lets tests use their own save file.
    """

    def __init__(self, save_path=None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        self.clock = pygame.time.Clock()
        self.background = build_arena_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))
        self.hud = Hud()
        self.profile = Profile(SaveFile(save_path))
        self.new_run()
        self.running = True

    def new_run(self) -> None:
        """Start a run with the stats the current upgrades give."""
        self.world = World(self.profile.stats())
        self.result: RunResult | None = None        # set once, when the run ends

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
                    self.new_run()                            # restart
                else:
                    for index, slot in enumerate(self.world.loadout):
                        if event.key == slot.key:
                            self.world.cast(index, pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == config.MOVE_MOUSE_BUTTON:
                if not self.world.over:
                    self.world.command_move(event.pos, new_click=True)

    def update(self, dt: float) -> None:
        # Holding the move button keeps updating the destination.
        if not self.world.over and pygame.mouse.get_pressed()[config.MOVE_MOUSE_BUTTON - 1]:
            self.world.command_move(pygame.mouse.get_pos(), new_click=False)
        self.world.update(dt)
        if self.world.over and self.result is None:
            # The run just ended: bank its coins and best time (this saves the file).
            self.result = self.profile.record_run(self.world.survival_time, self.world.coins_picked)

    # --- Drawing ------------------------------------------------------------------------
    def draw(self) -> None:
        self.screen.fill(PALETTE.background)
        self.screen.blit(self.background, (0, 0))
        self.world.draw(self.screen)
        self.hud.draw(self.screen, self.world)
        if self.world.over:
            self.draw_game_over()

    def draw_game_over(self) -> None:
        self.screen.blit(self.overlay, (0, 0))
        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        cause = "a laser" if isinstance(self.world.killer, Laser) else "a bolt"
        draw_text(self.screen, "GAME OVER", "title", PALETTE.danger, shadow=True, center=(cx, cy - 70))
        draw_text(self.screen, f"You survived {fmt_time(self.world.survival_time)} (hit by {cause})", "subtitle",
                  PALETTE.text, shadow=True, center=(cx, cy))
        if self.result:
            r = self.result
            best = "NEW BEST TIME!" if r.new_best else f"Best {fmt_time(self.profile.best_time)}"
            draw_text(self.screen, best, "hint", PALETTE.warning if r.new_best else PALETTE.text_dim,
                      shadow=True, center=(cx, cy + 36))
            draw_text(self.screen, f"+{r.coins} coins ({r.picked_up} picked up, {r.bonus} for surviving)"
                                   f"   |   {self.profile.coins} total", "hint", PALETTE.coin,
                      shadow=True, center=(cx, cy + 64))
        draw_text(self.screen, "Press R to restart   |   Esc to quit", "hint", PALETTE.text_dim,
                  center=(cx, cy + 104))
