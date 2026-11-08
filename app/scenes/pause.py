"""The pause scene: the run frozen behind a small card."""

import pygame

from app.render.text import draw_text
from app.scenes.base import Scene, card_rect, dim, draw_card
from app.scenes.play import PlayScene
from app.theme.palette import PALETTE
from app.theme.styles import BUTTON_WIDTH, CARD_PAD
from app.ui.widgets import Button, ButtonList
from app.util.timefmt import fmt_time


class PauseScene(Scene):
    """Nothing updates while paused, so the run continues exactly where it stopped."""

    def __init__(self, game, play: PlayScene) -> None:
        super().__init__(game)
        self.play = play
        self.card = card_rect(BUTTON_WIDTH + CARD_PAD * 2, 390)
        self.buttons = ButtonList([
            Button("Resume", self.resume, hotkey=game.settings.keybinds["pause"], primary=True),
            Button("Settings", game.open_settings),
            Button("Restart", game.start_run, hotkey="r"),
            Button("Main menu", game.open_main_menu, hotkey="m"),
        ], center=(self.card.centerx, self.card.bottom - CARD_PAD - 114))

    def resume(self) -> None:
        self.game.scene = self.play

    def handle_event(self, event: pygame.event.Event) -> None:
        self.buttons.handle_event(event)

    def update(self, dt: float) -> None:
        self.buttons.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world(surface)
        dim(surface, 150)
        draw_card(surface, self.card)
        cx = self.card.centerx
        draw_text(surface, "PAUSED", "heading", PALETTE.text, shadow=True, midtop=(cx, self.card.top + CARD_PAD))
        draw_text(surface, f"Survived {fmt_time(self.game.world.survival_time)} so far", "small",
                  PALETTE.text_dim, midtop=(cx, self.card.top + CARD_PAD + 52))
        self.buttons.draw(surface)
