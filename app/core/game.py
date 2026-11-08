"""The Game: owns the window, the main loop, the profile and the current scene."""

import pygame

from app import config
from app.core.settings import Settings
from app.core.storage import SaveFile
from app.core.world import World
from app.meta import APP_NAME
from app.progression.profile import Profile, RunResult
from app.render.arena import build_arena_background
from app.scenes.base import Scene
from app.scenes.game_over import GameOverScene
from app.scenes.guide import GuideScene
from app.scenes.main_menu import MainMenuScene
from app.scenes.pause import PauseScene
from app.scenes.play import PlayScene
from app.scenes.settings import SettingsScene
from app.scenes.shop import ShopScene
from app.theme.palette import PALETTE
from app.ui.hud import Hud


class Game:
    """Creates the window and runs a frame-rate independent main loop.

    Each frame: handle input -> update by ``dt`` seconds -> draw, all passed on
    to the current ``scene``. A run lives in a ``World``; the ``Profile``
    (coins, upgrades, best time) and the ``Settings`` outlive runs and share
    one save file. Every run is banked exactly
    once, however it ends: hit, restarted, left for the menu, or the window
    closed. ``save_path`` lets tests use their own save file.
    """

    def __init__(self, save_path=None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        self.clock = pygame.time.Clock()
        self.background = build_arena_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.hud = Hud()
        save_file = SaveFile(save_path)
        self.profile = Profile(save_file)
        self.settings = Settings(save_file)
        self.world = self.new_world()
        self.result: RunResult | None = None        # what the last banked run was worth
        self.in_run = False                         # a run has started and is not banked yet
        self.scene: Scene = MainMenuScene(self)
        self.running = True

    def new_world(self) -> World:
        """A run with the stats the current upgrades give and the player's key bindings."""
        return World(self.profile.stats(), self.settings.keybinds)

    # --- Navigation (called by scenes) --------------------------------------------------------
    def start_run(self) -> None:
        self.bank_run()
        self.world = self.new_world()
        self.result = None
        self.in_run = True
        self.scene = PlayScene(self)

    def pause(self) -> None:
        if isinstance(self.scene, PlayScene):
            self.scene = PauseScene(self, self.scene)

    def end_run(self) -> None:
        """The player was hit: bank the run and show what it was worth."""
        self.bank_run()
        self.scene = GameOverScene(self)

    def open_main_menu(self) -> None:
        self.bank_run()
        self.scene = MainMenuScene(self)

    def open_shop(self) -> None:
        """The shop returns to whichever screen opened it."""
        self.scene = ShopScene(self, back=self.scene)

    def open_settings(self) -> None:
        self.scene = SettingsScene(self, back=self.scene)

    def open_guide(self) -> None:
        self.scene = GuideScene(self, back=self.scene)

    def quit(self) -> None:
        self.bank_run()
        self.running = False

    def bank_run(self) -> None:
        """Add the current run's coins and time to the profile (saves the file). Safe to call twice."""
        if self.in_run:
            self.in_run = False
            self.result = self.profile.record_run(self.world.survival_time, self.world.coins_picked)

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
                self.quit()
            elif event.type == pygame.WINDOWFOCUSLOST:
                self.scene.on_focus_lost()
            else:
                self.scene.handle_event(event)

    def update(self, dt: float) -> None:
        self.scene.update(dt)

    # --- Drawing ------------------------------------------------------------------------
    def draw(self) -> None:
        self.scene.draw(self.screen)

    def draw_world(self, surface: pygame.Surface) -> None:
        """The arena, the run and the HUD: drawn by play, and behind the pause and game over cards."""
        surface.fill(PALETTE.background)
        surface.blit(self.background, (0, 0))
        self.world.draw(surface)
        fps = self.clock.get_fps() if self.settings.options["show_fps"] else None
        self.hud.draw(surface, self.world, fps)
