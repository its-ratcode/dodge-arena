"""The Skill base class: a cooldown plus a cast."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygame.math import Vector2

from app.theme.palette import PALETTE
from app.util.mathx import Color

if TYPE_CHECKING:                       # type hints only: avoids a circular import at runtime
    from app.core.world import World


class Skill:
    """Base class for everything the player can cast.

    A subclass sets ``name`` and ``cooldown``, picks its ``color`` from the
    palette and implements ``cast(world, aim)``. Returning ``False`` from
    ``cast`` cancels it without starting the cooldown.
    """

    name = "Skill"
    cooldown = 1.0                      # s

    def __init__(self) -> None:
        self.remaining = 0.0            # s left on the cooldown

    @property
    def color(self) -> Color:
        """Read at draw time so palette changes apply immediately."""
        return PALETTE.text

    @property
    def ready(self) -> bool:
        return self.remaining <= 0

    @property
    def cooldown_fraction(self) -> float:
        """1 right after casting -> 0 when ready."""
        return self.remaining / self.cooldown if self.cooldown > 0 else 0.0

    def update(self, dt: float) -> None:
        self.remaining = max(0.0, self.remaining - dt)

    def try_cast(self, world: World, aim: Vector2) -> bool:
        """Cast if ready. ``aim`` is a unit vector from the player toward the cursor."""
        if not self.ready or self.cast(world, aim) is False:
            return False
        self.remaining = self.cooldown
        return True

    def cast(self, world: World, aim: Vector2) -> bool | None:
        raise NotImplementedError
