"""Shape helpers that pygame.draw doesn't provide directly."""

import pygame

from app.util.mathx import Color, clamp


def draw_alpha_circle(surface: pygame.Surface, color: Color, center, radius: float,
                      alpha: float = 255, width: int = 0) -> None:
    """Draw a translucent circle.

    pygame.draw ignores alpha on the window surface, so the circle is drawn on a
    small temporary transparent surface and blitted on top.
    """
    radius = int(radius)
    if radius <= 0 or alpha <= 0 or (width and width >= radius):
        return
    size = radius * 2 + 2
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(temp, (*color, int(clamp(alpha, 0, 255))), (radius + 1, radius + 1), radius, width)
    surface.blit(temp, (int(center[0]) - radius - 1, int(center[1]) - radius - 1))
