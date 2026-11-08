"""Interface widgets: buttons, settings rows, and groups that work with mouse and keyboard."""

from collections.abc import Callable

import pygame
from pygame.math import Vector2

from app.render.icons import draw_icon
from app.render.shapes import draw_glow, draw_panel
from app.render.text import draw_keycap, draw_text, text_size
from app.theme.palette import PALETTE
from app.theme.styles import BUTTON_GAP, BUTTON_HEIGHT, BUTTON_WIDTH, PANEL_STYLES
from app.util.keys import key_label
from app.util.mathx import Color, lerp_color

# --- Menu sounds ---------------------------------------------------------------------------------
# Widgets don't know about audio. The Game plugs a player in once with set_ui_sound();
# until then (and in tests) sounds are silently skipped.
_ui_sound: Callable[[str], object] = lambda name: None


def set_ui_sound(play: Callable[[str], object]) -> None:
    global _ui_sound
    _ui_sound = play


def play_ui_sound(name: str) -> None:
    """"hover", "click", "back", "tick", "error", "buy", "sell"."""
    _ui_sound(name)


class Button:
    """A clickable box with a label, an optional icon and an optional hotkey keycap.

    ``primary`` buttons use the accent color for the main action of a screen.
    A disabled button can still be focused but does nothing (it plays an error
    sound). ``highlight`` eases between 0 and 1 so hovering fades in instead
    of popping. ``sound`` is the menu sound it makes when used.
    """

    def __init__(self, label: str | Callable[[], str], action: Callable[[], None], hotkey: str | None = None,
                 primary: bool = False, icon: str | None = None, style: str = "button",
                 size: tuple[int, int] = (BUTTON_WIDTH, BUTTON_HEIGHT), sound: str = "click") -> None:
        self._label = label                 # a string, or a function for labels that change (prices)
        self.action = action
        self.hotkey = hotkey
        self.hotkey_code = pygame.key.key_code(hotkey) if hotkey else None
        self.primary = primary
        self.icon = icon
        self.style = style
        self.sound = sound
        self.enabled = True
        self.rect = pygame.Rect((0, 0), size)
        self.highlight = 0.0
        self.pressed = False

    @property
    def label(self) -> str:
        return self._label() if callable(self._label) else self._label

    def activate(self) -> None:
        if self.enabled:
            play_ui_sound(self.sound)
            self.action()
        else:
            play_ui_sound("error")

    def update(self, dt: float, focused: bool) -> None:
        target = 1.0 if focused else 0.0
        step = dt * 10
        self.highlight += max(-step, min(step, target - self.highlight))

    # --- Drawing ---------------------------------------------------------------------------
    def accent(self) -> Color:
        return PALETTE.accent if self.primary else PALETTE.text_dim

    def draw_frame(self, surface: pygame.Surface) -> pygame.Rect:
        """Glow, panel and border; returns the rect to draw the content in."""
        rect = self.rect.move(0, 2) if self.pressed else self.rect      # sinks while held down
        h = self.highlight if self.enabled else self.highlight * 0.4
        if h > 0:
            draw_glow(surface, self.accent(), rect.center, rect.width * 0.45, int(70 * h))
        draw_panel(surface, rect, "button")
        base = PALETTE.accent if self.primary and self.enabled else PALETTE.line
        pygame.draw.rect(surface, lerp_color(base, PALETTE.text, h * 0.6), rect, 2 if self.primary or h > 0.5 else 1,
                         border_radius=PANEL_STYLES["button"].radius)
        return rect

    def text_color(self) -> Color:
        if not self.enabled:
            return PALETTE.text_faint
        return lerp_color(self.accent(), PALETTE.text, self.highlight)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.draw_frame(surface)
        label, color = self.label, self.text_color()
        if self.icon:
            # Icon and label centered together as one row.
            width = 22 + text_size(label, self.style)[0]
            left = rect.centerx - width // 2
            draw_icon(surface, self.icon, (left + 8, rect.centery), 18, color)
            draw_text(surface, label, self.style, color, shadow=True, midleft=(left + 22, rect.centery))
        else:
            draw_text(surface, label, self.style, color, shadow=True, center=rect.center)
        if self.hotkey:
            draw_keycap(surface, key_label(self.hotkey), midright=(rect.right - 12, rect.centery))


# --- Settings rows ---------------------------------------------------------------------------
class SettingRow(Button):
    """A full-width row: a label on the left, its current value on the right.
    ``desc`` is a sentence the settings screen shows while the row is focused."""

    def __init__(self, label: str, action: Callable[[], None], value: Callable[[], str],
                 size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, action, size=size, sound="tick")
        self.value = value
        self.desc = desc

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.draw_frame(surface)
        draw_text(surface, self.label, "button", self.text_color(), shadow=True, midleft=(rect.x + 16, rect.centery))
        self.draw_value(surface, rect)

    def draw_value(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        draw_text(surface, f"<  {self.value()}  >", "small", PALETTE.text, midright=(rect.right - 16, rect.centery))


class ChoiceRow(SettingRow):
    """Steps through a list of values: activating goes forward, Left / Right step either way."""

    def __init__(self, label: str, change: Callable[[int], None], value: Callable[[], str],
                 size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, lambda: change(1), value, size, desc)
        self.change = change


class VolumeRow(ChoiceRow):
    """A volume from 0 to 100%, shown as ten segments plus the number."""

    def __init__(self, label: str, change: Callable[[int], None], percent: Callable[[], int],
                 size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, change, lambda: f"{percent()}%", size, desc)
        self.percent = percent

    def draw_value(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        text = draw_text(surface, self.value(), "small", PALETTE.text, midright=(rect.right - 16, rect.centery))
        filled = self.percent() // 10
        for i in range(10):
            seg = pygame.Rect(0, 0, 8, 14)
            seg.midright = (text.left - 14 - (9 - i) * 11, rect.centery)
            pygame.draw.rect(surface, PALETTE.accent if i < filled else PALETTE.track, seg, border_radius=2)


class ColorRow(ChoiceRow):
    """A choice of color: shows a swatch of the color in use next to its name."""

    def __init__(self, label: str, change: Callable[[int], None], value: Callable[[], str],
                 color: Callable[[], Color], size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, change, value, size, desc)
        self.color = color

    def draw_value(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        text = draw_text(surface, f"<  {self.value()}  >", "small", PALETTE.text,
                         midright=(rect.right - 16, rect.centery))
        swatch = (text.left - 14, rect.centery)
        pygame.draw.circle(surface, self.color(), swatch, 8)
        pygame.draw.circle(surface, PALETTE.text_dim, swatch, 8, 1)


class KeyBindRow(SettingRow):
    """Shows the bound key as a keycap, or a prompt while waiting for a new key."""

    def __init__(self, label: str, action: Callable[[], None], key_name: Callable[[], str],
                 waiting: Callable[[], bool], size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, action, key_name, size, desc)
        self.waiting = waiting

    def draw_value(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self.waiting():
            draw_text(surface, "Press a key...  (Esc cancels)", "small", PALETTE.warning,
                      midright=(rect.right - 16, rect.centery))
        else:
            draw_keycap(surface, key_label(self.value()), midright=(rect.right - 16, rect.centery))


class ToggleRow(SettingRow):
    """An on/off switch."""

    def __init__(self, label: str, action: Callable[[], None], is_on: Callable[[], bool],
                 size: tuple[int, int], desc: str = "") -> None:
        super().__init__(label, action, lambda: "On" if is_on() else "Off", size, desc)
        self.is_on = is_on

    def draw_value(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        track = pygame.Rect(0, 0, 44, 22)
        track.midright = (rect.right - 16, rect.centery)
        on = self.is_on()
        pygame.draw.rect(surface, PALETTE.accent if on else PALETTE.track, track, border_radius=11)
        knob_x = track.right - 11 if on else track.left + 11
        pygame.draw.circle(surface, PALETTE.text if on else PALETTE.text_dim, (knob_x, track.centery), 8)


class TabButton(Button):
    """A tab: plain text with an accent underline when it is the open tab."""

    def __init__(self, label: str, action: Callable[[], None], is_open: Callable[[], bool],
                 size: tuple[int, int]) -> None:
        super().__init__(label, action, size=size, sound="tick")
        self.is_open = is_open

    def draw(self, surface: pygame.Surface) -> None:
        open_ = self.is_open()
        if self.highlight > 0:
            draw_glow(surface, PALETTE.accent, self.rect.center, self.rect.width * 0.4, int(40 * self.highlight))
        color = PALETTE.text if open_ else lerp_color(PALETTE.text_dim, PALETTE.text, self.highlight)
        draw_text(surface, self.label, "button", color, shadow=True, center=self.rect.center)
        if open_:
            line = pygame.Rect(0, 0, self.rect.width - 24, 3)
            line.midbottom = self.rect.midbottom
            pygame.draw.rect(surface, PALETTE.accent, line, border_radius=2)


# --- Groups ---------------------------------------------------------------------------------
DIRECTIONS = {pygame.K_UP: Vector2(0, -1), pygame.K_DOWN: Vector2(0, 1),
              pygame.K_LEFT: Vector2(-1, 0), pygame.K_RIGHT: Vector2(1, 0)}


class ButtonGroup:
    """Widgets placed anywhere on screen, sharing one keyboard focus.

    Mouse: hover focuses, click (press and release on the same widget) activates.
    Keyboard: the arrow keys move the focus to the nearest widget in that
    direction (so grids work too), Tab cycles in order, Enter or Space
    activates, and a widget's hotkey activates it directly.
    """

    def __init__(self, buttons: list[Button]) -> None:
        self.buttons = buttons
        self.focus = 0
        self._sounded_focus = 0             # the focus the last hover sound was played for

    def set_focus(self, index: int, sound: bool = False) -> None:
        """Move the focus from code (not from the player), silently unless ``sound``."""
        self.focus = index
        if not sound:
            self._sounded_focus = index

    def _button_at(self, pos) -> int | None:
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(pos):
                return i
        return None

    def _nearest(self, direction: Vector2) -> int | None:
        """The closest widget whose center lies in ``direction``; sideways distance counts double."""
        here = Vector2(self.buttons[self.focus].rect.center)
        best, best_score = None, float("inf")
        for i, button in enumerate(self.buttons):
            offset = Vector2(button.rect.center) - here
            ahead = offset.dot(direction)
            if i == self.focus or ahead <= 0:
                continue
            score = ahead + 2 * abs(offset.cross(direction))
            if score < best_score:
                best, best_score = i, score
        return best

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
                self.buttons[index].activate()
                return True
        elif event.type == pygame.KEYDOWN:
            for button in self.buttons:
                if button.hotkey_code is not None and event.key == button.hotkey_code:
                    button.activate()
                    return True
            if event.key in DIRECTIONS:
                index = self._nearest(DIRECTIONS[event.key])
                if index is not None:
                    self.focus = index
                return True
            if event.key == pygame.K_TAB:
                step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                self.focus = (self.focus + step) % len(self.buttons)
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.buttons[self.focus].activate()
                return True
        return False

    def update(self, dt: float) -> None:
        if self.focus != self._sounded_focus:              # focus moved (mouse or keys): a soft tick
            self._sounded_focus = self.focus
            play_ui_sound("hover")
        for i, button in enumerate(self.buttons):
            button.update(dt, i == self.focus)

    def draw(self, surface: pygame.Surface) -> None:
        for button in self.buttons:
            button.draw(surface)


class ButtonList(ButtonGroup):
    """Buttons stacked vertically and centered on ``center``. Up/Down wrap around at the ends."""

    def __init__(self, buttons: list[Button], center: tuple[int, int]) -> None:
        super().__init__(buttons)
        self.layout(center)

    def layout(self, center: tuple[int, int]) -> None:
        total = len(self.buttons) * BUTTON_HEIGHT + (len(self.buttons) - 1) * BUTTON_GAP
        y = center[1] - total // 2
        for button in self.buttons:
            button.rect.midtop = (center[0], y)
            y += BUTTON_HEIGHT + BUTTON_GAP

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_DOWN):
            step = 1 if event.key == pygame.K_DOWN else -1
            self.focus = (self.focus + step) % len(self.buttons)
            return True
        return super().handle_event(event)
