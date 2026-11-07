"""The color palette.

All colors live on one shared ``PALETTE`` object that the drawing code reads
at draw time, so changing a color here changes it everywhere.
"""

from dataclasses import dataclass

from app.util.mathx import Color, lerp_color


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

    # Threats
    bolt: Color = (225, 60, 70)
    bolt_core: Color = (255, 150, 140)
    bolt_front: Color = (255, 232, 210)      # bright leading edge shows the flight direction
    laser: Color = (255, 110, 196)
    laser_core: Color = (255, 250, 255)

    # Abilities
    shield: Color = (120, 200, 255)
    wall: Color = (150, 110, 240)
    wall_outline: Color = (230, 210, 255)
    dash: Color = (80, 236, 214)

    # Utility spells
    sprint: Color = (255, 215, 70)
    blink: Color = (255, 236, 130)

    # Text and feedback
    text: Color = (236, 240, 248)
    text_dim: Color = (162, 174, 196)
    accent: Color = (64, 206, 226)           # low danger
    warning: Color = (250, 196, 80)          # medium danger
    danger: Color = (236, 76, 88)            # high danger, game over
    track: Color = (36, 45, 64)              # empty part of progress bars


PALETTE = Palette()


def danger_color(level: float) -> Color:
    """Color for a danger level 0..1: accent -> warning -> danger.

    Going through a middle color avoids the muddy grey you get when blending
    cyan straight into red.
    """
    if level < 0.5:
        return lerp_color(PALETTE.accent, PALETTE.warning, level * 2)
    return lerp_color(PALETTE.warning, PALETTE.danger, (level - 0.5) * 2)
