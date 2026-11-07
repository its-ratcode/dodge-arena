"""The player: a circle that walks in a straight line to where you click."""

import pygame
from pygame.math import Vector2

from app import config
from app.theme.palette import PALETTE
from app.util.mathx import clamp


class Player:
    """Moves toward ``destination`` at a constant speed and stops exactly there."""

    def __init__(self, pos) -> None:
        self.pos = Vector2(pos)
        self.destination = Vector2(pos)
        self.facing = Vector2(1, 0)            # last movement direction
        self.radius = config.PLAYER_RADIUS
        self.speed = config.PLAYER_SPEED

    # --- Movement -----------------------------------------------------------------------
    def clamp_to_arena(self, point) -> Vector2:
        """Keep a point inside the window so the whole circle stays visible."""
        return Vector2(clamp(point[0], self.radius, config.SCREEN_WIDTH - self.radius),
                       clamp(point[1], self.radius, config.SCREEN_HEIGHT - self.radius))

    def move_to(self, point) -> None:
        """Set a new walk destination."""
        self.destination = self.clamp_to_arena(point)

    def update(self, dt: float) -> None:
        to_target = self.destination - self.pos
        distance = to_target.length()
        step = self.speed * dt
        if distance > 0:
            self.facing = to_target / distance
        if distance <= step:
            self.pos = Vector2(self.destination)      # arrive exactly, no overshoot
        else:
            self.pos += to_target * (step / distance)

    # --- Drawing ------------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, PALETTE.player, self.pos, self.radius)
        highlight = self.pos - Vector2(self.radius, self.radius) * 0.3
        pygame.draw.circle(surface, PALETTE.player_light, highlight, self.radius * 0.45)
        pygame.draw.circle(surface, PALETTE.player_outline, self.pos, self.radius, 2)
        # A small notch showing which way the player last moved.
        side = Vector2(-self.facing.y, self.facing.x)
        base = self.pos + self.facing * (self.radius + 1)
        tip = self.pos + self.facing * (self.radius + 7)
        pygame.draw.polygon(surface, PALETTE.player_outline, [tip, base + side * 5, base - side * 5])
