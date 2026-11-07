"""Text rendering with cached fonts."""

import pygame

from app.util.mathx import Color

FONT_STACK = "bahnschrift,segoeui,arial"     # first one installed is used
_fonts: dict[tuple[int, bool], pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(FONT_STACK, size, bold=bold)
    return _fonts[key]


def draw_text(surface: pygame.Surface, text: str, size: int, color: Color,
              bold: bool = False, **anchor) -> pygame.Rect:
    """Draw text positioned by any pygame.Rect anchor, e.g. ``center=(x, y)``."""
    image = get_font(size, bold).render(text, True, color)
    rect = image.get_rect(**anchor)
    surface.blit(image, rect)
    return rect
