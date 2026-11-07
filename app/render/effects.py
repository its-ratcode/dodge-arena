"""Short-lived visual effects."""

import pygame
from pygame.math import Vector2

from app import config
from app.render.shapes import draw_alpha_circle
from app.theme.palette import PALETTE
from app.util.mathx import lerp_color


class Effect:
    """Base class: something drawn for ``duration`` seconds, then removed."""

    def __init__(self, duration: float) -> None:
        self.duration = duration
        self.age = 0.0

    @property
    def progress(self) -> float:
        """0 when created -> 1 when finished."""
        return min(1.0, self.age / self.duration)

    @property
    def alive(self) -> bool:
        return self.age < self.duration

    def update(self, dt: float) -> None:
        self.age += dt

    def draw(self, surface: pygame.Surface) -> None:
        pass


class ClickMarker(Effect):
    """A shrinking ring with four inward ticks where the player clicked to move."""

    def __init__(self, pos) -> None:
        super().__init__(config.CLICK_MARKER_DURATION)
        self.pos = Vector2(pos)

    def draw(self, surface: pygame.Surface) -> None:
        t = self.progress
        radius = 3 + config.CLICK_MARKER_RADIUS * (1 - t)
        draw_alpha_circle(surface, PALETTE.marker, self.pos, radius, alpha=255 * (1 - t), width=2)
        tick_color = lerp_color(PALETTE.marker, PALETTE.arena_center, t)
        for angle in (45, 135, 225, 315):
            d = Vector2(1, 0).rotate(angle)
            pygame.draw.line(surface, tick_color, self.pos + d * (radius + 6), self.pos + d * (radius + 1), 2)


class Burst(Effect):
    """An expanding, fading ring: feedback for a blocked hit or a bolt hitting a wall."""

    def __init__(self, pos, color, scale: float = 1.0) -> None:
        super().__init__(config.BURST_DURATION)
        self.pos = Vector2(pos)
        self.color = color
        self.scale = scale

    def draw(self, surface: pygame.Surface) -> None:
        t = self.progress
        radius = (10 + 34 * t) * self.scale
        draw_alpha_circle(surface, self.color, self.pos, radius, alpha=230 * (1 - t), width=3)
