"""Procedural vector icons, drawn with pygame.draw (no image files needed).

Each icon is designed in a box from -1 to 1 on both axes and scaled to
``size`` px, so it stays sharp at any size and takes any color.
"""

import pygame

from app.theme.palette import PALETTE
from app.util.mathx import Color


def draw_icon(surface: pygame.Surface, name: str, center, size: float, color: Color) -> None:
    cx, cy = center
    s = size / 2
    w = max(2, round(size / 11))                   # line width grows with the icon

    def p(x: float, y: float) -> tuple[float, float]:
        """Icon-box coordinates -> screen coordinates."""
        return cx + x * s, cy + y * s

    if name == "shield":
        pygame.draw.polygon(surface, color, [p(-0.72, -0.78), p(0.72, -0.78), p(0.72, 0.05),
                                             p(0, 0.88), p(-0.72, 0.05)], w)
        pygame.draw.line(surface, color, p(0, -0.5), p(0, 0.5), w)
    elif name == "wall":
        # Three rows of bricks with staggered joints.
        for row, y in enumerate((-0.62, -0.02, 0.58)):
            brick = pygame.Rect(0, 0, 1.7 * s, max(3, 0.42 * s))
            brick.center = (round(cx), round(cy + y * s))
            pygame.draw.rect(surface, color, brick, border_radius=2)
            jx = -0.25 if row % 2 else 0.25
            pygame.draw.line(surface, PALETTE.panel_bottom, p(jx, y - 0.2), p(jx, y + 0.2), max(1, w - 1))
    elif name == "dash":
        # Double chevron.
        for off in (-0.38, 0.32):
            pygame.draw.lines(surface, color, False, [p(off - 0.3, -0.62), p(off + 0.3, 0), p(off - 0.3, 0.62)], w + 1)
    elif name == "sprint":
        # Speed lines behind an arrowhead.
        for y, x0 in ((-0.45, -0.9), (0, -0.7), (0.45, -0.9)):
            pygame.draw.line(surface, color, p(x0, y), p(0.05, y), w)
        pygame.draw.polygon(surface, color, [p(0.15, -0.6), p(0.92, 0), p(0.15, 0.6)])
    elif name == "blink":
        # A dotted start, then a solid jump arrow.
        for x0, x1 in ((-0.95, -0.72), (-0.58, -0.32)):
            pygame.draw.line(surface, color, p(x0, 0), p(x1, 0), w)
        pygame.draw.line(surface, color, p(-0.15, 0), p(0.85, 0), w)
        pygame.draw.lines(surface, color, False, [p(0.4, -0.42), p(0.88, 0), p(0.4, 0.42)], w)
    else:
        # Unknown name: a plain ring, so a missing icon is visible but harmless.
        pygame.draw.circle(surface, color, (cx, cy), max(3, int(s * 0.7)), w)


ICON_NAMES = ("shield", "wall", "dash", "sprint", "blink")
"""Every icon drawn above."""
