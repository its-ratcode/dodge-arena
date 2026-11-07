"""The color palette.

All colors live on one shared ``PALETTE`` object that the drawing code reads
at draw time, so changing a color here changes it everywhere.
"""

from dataclasses import dataclass

from app.util.mathx import Color


@dataclass
class Palette:
    """Every color the game uses, grouped by purpose."""

    # Surfaces
    background: Color = (7, 10, 16)          # behind everything
    arena_center: Color = (19, 29, 38)
    arena_edge: Color = (8, 12, 18)
    grid_line: Color = (255, 255, 255)       # drawn with low alpha over the arena
    border: Color = (33, 43, 62)

    # Player
    player: Color = (70, 170, 255)
    player_light: Color = (160, 210, 255)    # highlight
    player_outline: Color = (215, 238, 255)
    marker: Color = (90, 230, 140)           # click-to-move marker


PALETTE = Palette()
