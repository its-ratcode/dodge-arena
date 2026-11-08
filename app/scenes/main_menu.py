"""The main menu: title, your records, and the way into a run."""

import random

import pygame
from pygame.math import Vector2

from app import config
from app.core.settings import MOVE_BUTTONS
from app.entities.bolt import Bolt
from app.meta import APP_NAME, VERSION
from app.render.icons import draw_icon
from app.render.shapes import draw_glow, draw_panel
from app.render.text import draw_text, text_size
from app.scenes.base import Scene, dim
from app.theme.palette import PALETTE
from app.ui.widgets import Button, ButtonList
from app.util.keys import key_label
from app.util.timefmt import fmt_time

DEMO_BOLT_INTERVAL = 0.45      # s between decorative bolts crossing the background
DEMO_BOLT_SPEED = 260          # px/s


class MainMenuScene(Scene):
    """Harmless bolts drift across the arena behind the menu to show what the game is about."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.age = 0.0
        self.bolts: list[Bolt] = []
        self.bolt_timer = 0.0
        self.buttons = ButtonList([
            Button("Play", game.start_run, primary=True),
            Button("Shop", game.open_shop, hotkey="s"),
            Button("Settings", game.open_settings),
            Button("Quit", game.quit, hotkey="escape"),
        ], center=(config.SCREEN_WIDTH // 2, 480))

    def controls_hint(self) -> str:
        """The controls line at the bottom, built from the player's current bindings."""
        s = self.game.settings
        keys = {action: key_label(name) for action, name in s.keybinds.items()}
        return (f"{MOVE_BUTTONS[s.move_button]} move   |   {keys['shield']} {keys['wall']} {keys['dash']} abilities"
                f"   |   {keys['sprint']} {keys['blink']} utility spells   |   {keys['powerup']} power-up"
                f"   |   {keys['pause']} pause")

    def handle_event(self, event: pygame.event.Event) -> None:
        self.buttons.handle_event(event)

    def update(self, dt: float) -> None:
        self.age += dt
        self.buttons.update(dt)
        self.bolt_timer -= dt
        if self.bolt_timer <= 0:
            self.bolt_timer += DEMO_BOLT_INTERVAL
            self.bolts.append(self.demo_bolt())
        for bolt in self.bolts:
            bolt.update(dt)
        self.bolts = [b for b in self.bolts if not b.is_off_screen()]

    @staticmethod
    def demo_bolt() -> Bolt:
        """A slow bolt from a random edge toward a random point in the arena."""
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        edge = random.choice(((random.uniform(0, w), -40), (random.uniform(0, w), h + 40),
                              (-40, random.uniform(0, h)), (w + 40, random.uniform(0, h))))
        target = Vector2(random.uniform(w * 0.2, w * 0.8), random.uniform(h * 0.2, h * 0.8))
        return Bolt(edge, target, DEMO_BOLT_SPEED)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE.background)
        surface.blit(self.game.background, (0, 0))
        for bolt in self.bolts:
            bolt.draw(surface)
        dim(surface, 140)
        cx = config.SCREEN_WIDTH // 2

        draw_glow(surface, PALETTE.accent, (cx, 145), 260, 45)
        draw_text(surface, APP_NAME.upper(), "title", PALETTE.text, shadow=True, center=(cx, 140))
        draw_text(surface, "Dodge the bolts. Outlast the lasers. Survive.", "subtitle", PALETTE.text_dim,
                  center=(cx, 198))
        self.draw_records(surface, cx, 250)
        self.buttons.draw(surface)

        draw_text(surface, self.controls_hint(), "small", PALETTE.text_faint, midbottom=(cx, config.SCREEN_HEIGHT - 20))
        draw_text(surface, f"v{VERSION}", "tiny", PALETTE.text_faint,
                  bottomright=(config.SCREEN_WIDTH - 14, config.SCREEN_HEIGHT - 20))

    def draw_records(self, surface: pygame.Surface, cx: int, y: int) -> None:
        """Two chips: best time and coins."""
        profile = self.game.profile
        best = fmt_time(profile.best_time) if profile.best_time > 0 else "--"
        for i, (label, value, color) in enumerate((("BEST TIME", best, PALETTE.text),
                                                   ("COINS", str(profile.coins), PALETTE.coin))):
            chip = pygame.Rect(0, 0, 170, 62)
            chip.center = (cx + (i * 2 - 1) * 95, y + 31)
            draw_panel(surface, chip, "chip")
            draw_text(surface, label, "label", PALETTE.text_faint, midtop=(chip.centerx, chip.top + 9))
            if label == "COINS":
                width = 24 + text_size(value, "cooldown")[0]
                left = chip.centerx - width // 2
                draw_icon(surface, "coin", (left + 9, chip.top + 40), 18, PALETTE.coin)
                draw_text(surface, value, "cooldown", color, shadow=True, midleft=(left + 24, chip.top + 40))
            else:
                draw_text(surface, value, "cooldown", color, shadow=True, center=(chip.centerx, chip.top + 40))
