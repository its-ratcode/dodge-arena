"""Interface widgets: buttons and a vertical button list that works with mouse and keyboard."""

from collections.abc import Callable

import pygame

from app.render.shapes import draw_glow, draw_panel
from app.render.text import draw_keycap, draw_text
from app.theme.palette import PALETTE
from app.theme.styles import BUTTON_GAP, BUTTON_HEIGHT, BUTTON_WIDTH, PANEL_STYLES
from app.util.mathx import lerp_color

KEY_LABELS = {"escape": "ESC", "return": "ENTER"}      # short labels for long pygame key names


def key_label(key_name: str) -> str:
    """How a pygame key name is shown on a keycap: "escape" -> "ESC", "r" -> "R"."""
    return KEY_LABELS.get(key_name, key_name.upper())


class Button:
    """A clickable box with a label and an optional hotkey shown as a keycap.

    ``primary`` buttons use the accent color for the main action of a screen.
    ``highlight`` eases between 0 and 1 so hovering fades in instead of popping.
    """

    def __init__(self, label: str, action: Callable[[], None], hotkey: str | None = None,
                 primary: bool = False) -> None:
        self.label = label
        self.action = action
        self.hotkey = hotkey
        self.hotkey_code = pygame.key.key_code(hotkey) if hotkey else None
        self.primary = primary
        self.rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.highlight = 0.0
        self.pressed = False

    def update(self, dt: float, focused: bool) -> None:
        target = 1.0 if focused else 0.0
        step = dt * 10
        self.highlight += max(-step, min(step, target - self.highlight))

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect.move(0, 2) if self.pressed else self.rect      # sinks while held down
        accent = PALETTE.accent if self.primary else PALETTE.text_dim
        h = self.highlight
        if h > 0:
            draw_glow(surface, accent, rect.center, rect.width * 0.45, int(70 * h))
        draw_panel(surface, rect, "button")
        border = lerp_color(PALETTE.accent if self.primary else PALETTE.line, PALETTE.text, h * 0.6)
        pygame.draw.rect(surface, border, rect, 2 if self.primary or h > 0.5 else 1,
                         border_radius=PANEL_STYLES["button"].radius)
        text_color = lerp_color(accent if self.primary else PALETTE.text_dim, PALETTE.text, h)
        draw_text(surface, self.label, "button", text_color, shadow=True, center=rect.center)
        if self.hotkey:
            draw_keycap(surface, key_label(self.hotkey), midright=(rect.right - 12, rect.centery))


class ButtonList:
    """Buttons stacked vertically and centered on ``center``.

    Mouse: hover focuses, click (press and release on the same button) activates.
    Keyboard: Up/Down or Tab move the focus, Enter or Space activates, and each
    button's hotkey activates it directly.
    """

    def __init__(self, buttons: list[Button], center: tuple[int, int]) -> None:
        self.buttons = buttons
        self.focus = 0
        self.layout(center)

    def layout(self, center: tuple[int, int]) -> None:
        total = len(self.buttons) * BUTTON_HEIGHT + (len(self.buttons) - 1) * BUTTON_GAP
        y = center[1] - total // 2
        for button in self.buttons:
            button.rect.midtop = (center[0], y)
            y += BUTTON_HEIGHT + BUTTON_GAP

    @property
    def bounds(self) -> pygame.Rect:
        return self.buttons[0].rect.unionall([b.rect for b in self.buttons[1:]])

    def _button_at(self, pos) -> int | None:
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(pos):
                return i
        return None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if the event was used (so the screen can ignore it)."""
        if event.type == pygame.MOUSEMOTION:
            index = self._button_at(event.pos)
            if index is not None:
                self.focus = index
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._button_at(event.pos)
            if index is not None:
                self.focus = index
                self.buttons[index].pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            index = self._button_at(event.pos)
            was_pressed = index is not None and self.buttons[index].pressed
            for button in self.buttons:
                button.pressed = False
            if was_pressed:
                self.buttons[index].action()
                return True
        elif event.type == pygame.KEYDOWN:
            for button in self.buttons:
                if event.key == button.hotkey_code:
                    button.action()
                    return True
            if event.key in (pygame.K_DOWN, pygame.K_TAB):
                self.focus = (self.focus + 1) % len(self.buttons)
                return True
            if event.key == pygame.K_UP:
                self.focus = (self.focus - 1) % len(self.buttons)
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.buttons[self.focus].action()
                return True
        return False

    def update(self, dt: float) -> None:
        for i, button in enumerate(self.buttons):
            button.update(dt, i == self.focus)

    def draw(self, surface: pygame.Surface) -> None:
        for button in self.buttons:
            button.draw(surface)
