"""The color palette.

All colors live on one shared ``PALETTE`` object that the drawing code reads
at draw time, so changing a color here changes it everywhere.
"""

from dataclasses import dataclass

from app.util.mathx import Color


@dataclass
class Palette:
    """Every color the game uses, grouped by purpose."""

    background: Color = (7, 10, 16)          # behind everything
    arena_center: Color = (19, 29, 38)
    arena_edge: Color = (8, 12, 18)
    grid_line: Color = (255, 255, 255)       # drawn with low alpha over the arena
    border: Color = (33, 43, 62)


PALETTE = Palette()
