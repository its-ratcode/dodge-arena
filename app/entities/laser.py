"""Lasers: beams across the whole arena, aimed through the player's position."""

import pygame
from pygame.math import Vector2

from app import config
from app.theme.palette import PALETTE
from app.util.geometry import RotatedRect
from app.util.mathx import clamp


class Laser:
    """Three phases: warning (harmless telegraph) -> firing (deadly) -> fade (harmless).

    The beam passes through ``target`` (the player's position when it was cast)
    from a random angle, and is long enough to cross the whole arena.
    """

    def __init__(self, origin, target, warning_time: float) -> None:
        direction = Vector2(target) - Vector2(origin)
        self.shape = RotatedRect(target, direction, config.LASER_LENGTH, config.LASER_WIDTH)
        self.warning_time = warning_time
        self.age = 0.0

    @property
    def firing(self) -> bool:
        return self.warning_time <= self.age < self.warning_time + config.LASER_ACTIVE_TIME

    @property
    def alive(self) -> bool:
        return self.age < self.warning_time + config.LASER_ACTIVE_TIME + config.LASER_FADE_TIME

    def update(self, dt: float) -> None:
        self.age += dt

    def band(self, width: float) -> list[Vector2]:
        """Corners of a strip along the beam with the given width (for layered drawing)."""
        return RotatedRect(self.shape.center, self.shape.direction, self.shape.length, width).corners()

    def draw(self, layer: pygame.Surface) -> None:
        """Draw onto a transparent full-screen layer (alpha is needed for the glow)."""
        if self.age < self.warning_time:
            # Warning: an outlined lane plus a strip that widens until the beam fires.
            p = self.age / self.warning_time
            flicker = 20 if int(self.age * 20) % 2 == 0 else 0
            pygame.draw.polygon(layer, (*PALETTE.laser, 25 + int(35 * p)), self.band(config.LASER_WIDTH))
            pygame.draw.polygon(layer, (*PALETTE.laser, 150 + flicker), self.band(config.LASER_WIDTH), 2)
            pygame.draw.polygon(layer, (*PALETTE.laser, 60 + int(120 * p)),
                                self.band(max(2.0, config.LASER_WIDTH * p)))
        elif self.firing:
            # Firing: wide glow, colored body, white-hot core.
            pygame.draw.polygon(layer, (*PALETTE.laser, 90), self.band(config.LASER_WIDTH * 1.5))
            pygame.draw.polygon(layer, (*PALETTE.laser, 220), self.band(config.LASER_WIDTH))
            pygame.draw.polygon(layer, (*PALETTE.laser_core, 255), self.band(config.LASER_WIDTH * 0.35))
        else:
            # Fade-out. Clamped: a laser may age past its end before it is removed.
            f = clamp(1 - (self.age - self.warning_time - config.LASER_ACTIVE_TIME) / config.LASER_FADE_TIME,
                      0.0, 1.0)
            if f > 0:
                pygame.draw.polygon(layer, (*PALETTE.laser, int(180 * f)),
                                    self.band(max(2.0, config.LASER_WIDTH * f)))
