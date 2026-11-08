"""The game over scene: what the run was worth, and what to do next."""

import pygame

from app.entities.laser import Laser
from app.render.icons import draw_icon
from app.render.text import draw_text, text_size
from app.scenes.base import Scene, card_rect, dim, draw_card, ease_out
from app.theme.accessibility import wobble
from app.theme.palette import PALETTE
from app.theme.styles import BUTTON_GAP, BUTTON_HEIGHT, CARD_PAD
from app.ui.widgets import Button, ButtonList
from app.util.timefmt import fmt_time

CARD_DELAY = 0.45       # s the moment of death stays visible before the card appears
CARD_SLIDE = 0.3        # s for the card to slide into place
CARD_SIZE = (440, 490)


class GameOverScene(Scene):
    """Input is ignored until the card is in place, so keys mashed while dying
    can't skip it by accident."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.age = 0.0
        self.buttons = ButtonList([
            Button("Play again", game.start_run, hotkey="r", primary=True),
            Button("Shop", game.open_shop, hotkey="s"),
            Button("Main menu", game.open_main_menu, hotkey="escape"),
        ], center=(0, 0))

    @property
    def shown(self) -> float:
        """0 -> 1 as the card slides in."""
        return ease_out((self.age - CARD_DELAY) / CARD_SLIDE)

    def card(self) -> pygame.Rect:
        slide = wobble(30 * (1 - self.shown))             # with reduced motion it only fades in
        return card_rect(*CARD_SIZE, offset_y=round(slide))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.shown >= 1:
            self.buttons.handle_event(event)

    def update(self, dt: float) -> None:
        if self.age < CARD_DELAY <= self.age + dt and self.game.result and self.game.result.new_best:
            self.game.audio.play("new_best")               # a fanfare as the card arrives
        self.age += dt
        card = self.card()
        count = len(self.buttons.buttons)
        stack = BUTTON_HEIGHT * count + BUTTON_GAP * (count - 1)      # height of the button column
        self.buttons.layout((card.centerx, card.bottom - CARD_PAD - stack // 2))
        self.buttons.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world(surface)
        dim(surface, round(170 * self.shown))
        if self.shown <= 0:
            return
        world, result, profile = self.game.world, self.game.result, self.game.profile
        card = self.card()
        draw_card(surface, card)
        cx, y = card.centerx, card.top + CARD_PAD
        draw_text(surface, "GAME OVER", "heading", PALETTE.danger, shadow=True, midtop=(cx, y))
        if world.killer is not None:
            cause = "Hit by a laser" if isinstance(world.killer, Laser) else "Hit by a bolt"
        else:
            cause = "Run ended"
        draw_text(surface, cause, "small", PALETTE.text_dim, midtop=(cx, y + 50))
        draw_text(surface, fmt_time(world.survival_time), "stat", PALETTE.text, shadow=True, midtop=(cx, y + 80))
        if result.new_best:
            draw_text(surface, "NEW BEST TIME!", "label", PALETTE.warning, shadow=True, midtop=(cx, y + 124))
        elif not result.counted:
            draw_text(surface, "ASSISTS ON: NOT COUNTED FOR BEST TIME", "label", PALETTE.text_faint,
                      midtop=(cx, y + 124))
        else:
            draw_text(surface, f"BEST {fmt_time(profile.best_time)}", "label", PALETTE.text_faint,
                      midtop=(cx, y + 124))

        line_y = y + 152
        pygame.draw.line(surface, PALETTE.line, (card.left + CARD_PAD, line_y), (card.right - CARD_PAD, line_y))
        # Coins: icon and total on one centered row, the breakdown below.
        earned = f"+{result.coins} coins"
        width = 26 + text_size(earned, "button")[0]
        left = cx - width // 2
        draw_icon(surface, "coin", (left + 10, line_y + 30), 20, PALETTE.coin)
        draw_text(surface, earned, "button", PALETTE.coin, shadow=True, midleft=(left + 26, line_y + 30))
        draw_text(surface, f"{result.picked_up} picked up  +  {result.bonus} for surviving   |   "
                           f"{profile.coins} total", "small", PALETTE.text_dim, midtop=(cx, line_y + 48))
        self.buttons.draw(surface)
