"""The three abilities: Shield, Wall and Dash."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygame.math import Vector2

from app import config
from app.entities.wall import Wall
from app.skills.base import Skill
from app.theme.palette import PALETTE
from app.util.mathx import Color

if TYPE_CHECKING:
    from app.core.world import World


class Shield(Skill):
    """A bubble that blocks the next hit (bolt or laser) for a short time."""

    name = "Shield"
    cooldown = config.SHIELD_COOLDOWN

    @property
    def color(self) -> Color:
        return PALETTE.shield

    def cast(self, world: World, target: Vector2) -> None:
        world.player.add_shield(config.SHIELD_DURATION)


class WallSkill(Skill):
    """Raises a wall in front of the player, across the direction of the cursor."""

    name = "Wall"
    cooldown = config.WALL_COOLDOWN

    @property
    def color(self) -> Color:
        return PALETTE.wall

    def cast(self, world: World, target: Vector2) -> None:
        aim = world.aim_direction(target)
        center = world.player.pos + aim * config.WALL_DISTANCE
        world.walls.append(Wall(center, Vector2(-aim.y, aim.x)))


class Dash(Skill):
    """A fast, fixed-distance dash toward the cursor. You can still be hit on the way."""

    name = "Dash"
    cooldown = config.DASH_COOLDOWN

    @property
    def color(self) -> Color:
        return PALETTE.dash

    def cast(self, world: World, target: Vector2) -> None:
        aim = world.aim_direction(target)
        world.player.start_dash(world.player.pos + aim * config.DASH_RANGE, config.DASH_SPEED)
