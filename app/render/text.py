"""Text rendering with cached fonts, plus keycaps (a key binding drawn as a key)."""

import pygame

from app.theme.palette import PALETTE
from app.theme.styles import RADIUS_SM
from app.theme.typography import TEXT_STYLES, TextStyle
from app.util.mathx import Color, lerp_color

_fonts: dict[TextStyle, pygame.font.Font] = {}


def get_font(style: str) -> pygame.font.Font:
    """The font for a text style role from ``TEXT_STYLES`` (cached)."""
    spec = TEXT_STYLES[style]
    if spec not in _fonts:
        _fonts[spec] = pygame.font.SysFont(spec.font, spec.size, bold=spec.bold)
    return _fonts[spec]


def text_size(text: str, style: str) -> tuple[int, int]:
    return get_font(style).size(text)


def line_height(style: str) -> int:
    return get_font(style).get_linesize()


def wrap_text(text: str, style: str, width: int) -> list[str]:
    """Split ``text`` into lines no wider than ``width`` px, breaking between words.
    A single word longer than the width gets a line of its own."""
    font = get_font(style)
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}" if line else word
        if font.size(trial)[0] <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_text(surface: pygame.Surface, text: str, style: str, color: Color,
              shadow: bool = False, **anchor) -> pygame.Rect:
    """Draw text positioned by any pygame.Rect anchor, e.g. ``center=(x, y)``.

    ``shadow`` adds a dark copy 1 px below, which keeps text readable over busy
    backgrounds such as lasers.
    """
    font = get_font(style)
    image = font.render(text, True, color)
    rect = image.get_rect(**anchor)
    if shadow:
        surface.blit(font.render(text, True, PALETTE.key_shadow), rect.move(1, 2))
    surface.blit(image, rect)
    return rect


def draw_keycap(surface: pygame.Surface, label: str, **anchor) -> pygame.Rect:
    """A small raised key showing a binding, e.g. [Q]."""
    width = max(22, text_size(label, "key")[0] + 12)
    rect = pygame.Rect(0, 0, width, 20)
    for name, value in anchor.items():
        setattr(rect, name, value)
    pygame.draw.rect(surface, PALETTE.key_shadow, rect.move(0, 2), border_radius=RADIUS_SM)
    pygame.draw.rect(surface, PALETTE.key_face, rect, border_radius=RADIUS_SM)
    pygame.draw.rect(surface, lerp_color(PALETTE.key_face, PALETTE.text, 0.2), rect, 1, border_radius=RADIUS_SM)
    draw_text(surface, label, "key", PALETTE.text, center=rect.center)
    return rect
