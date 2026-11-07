"""Permanent upgrades bought with coins, and the run stats they produce.

To balance an upgrade, edit its row in ``UPGRADES``. To add one, add a row
and read its bonus in ``RunStats.from_levels``.
"""

from dataclasses import dataclass

from app import config


@dataclass(frozen=True)
class Upgrade:
    """One upgrade line. ``step`` is the effect of a single level."""

    id: str
    name: str
    max_level: int
    base_cost: int
    growth: float                       # each level costs ``growth`` times the previous one
    step: float

    def cost(self, level: int) -> int:
        """Price of going from ``level`` to ``level + 1``."""
        return round(self.base_cost * self.growth ** level)


UPGRADES: tuple[Upgrade, ...] = (
    Upgrade("boots", "Swift Boots", max_level=5, base_cost=15, growth=1.5, step=0.05),    # +5% speed
    Upgrade("haste", "Ability Haste", max_level=5, base_cost=20, growth=1.5, step=0.06),  # -6% Q/W/E cooldowns
    Upgrade("shield", "Thick Bubble", max_level=4, base_cost=15, growth=1.5, step=0.3),   # +0.3 s Shield
    Upgrade("wall", "Long Wall", max_level=4, base_cost=15, growth=1.5, step=25),         # +25 px Wall
    Upgrade("sprint", "Long Sprint", max_level=4, base_cost=15, growth=1.5, step=0.5),    # +0.5 s Sprint
    Upgrade("blink", "Far Blink", max_level=3, base_cost=25, growth=1.6, step=20),        # +20 px Blink
    Upgrade("magnet", "Coin Magnet", max_level=4, base_cost=10, growth=1.5, step=40),     # +40 px pull radius
)
UPGRADE_BY_ID = {u.id: u for u in UPGRADES}


@dataclass(frozen=True)
class RunStats:
    """Every upgrade-dependent number for one run, worked out once when it starts."""

    player_speed: float = config.PLAYER_SPEED
    cooldown_mult: float = 1.0          # applies to abilities only, not utility spells
    shield_duration: float = config.SHIELD_DURATION
    wall_length: float = config.WALL_LENGTH
    sprint_duration: float = config.SPRINT_DURATION
    blink_range: float = config.BLINK_RANGE
    magnet_radius: float = 0.0          # px; 0 = no magnet

    @classmethod
    def from_levels(cls, levels: dict[str, int]) -> "RunStats":
        def bonus(uid: str) -> float:
            return levels.get(uid, 0) * UPGRADE_BY_ID[uid].step

        return cls(player_speed=config.PLAYER_SPEED * (1 + bonus("boots")),
                   cooldown_mult=max(config.MIN_COOLDOWN_MULT, 1 - bonus("haste")),
                   shield_duration=config.SHIELD_DURATION + bonus("shield"),
                   wall_length=config.WALL_LENGTH + bonus("wall"),
                   sprint_duration=config.SPRINT_DURATION + bonus("sprint"),
                   blink_range=config.BLINK_RANGE + bonus("blink"),
                   magnet_radius=bonus("magnet"))
