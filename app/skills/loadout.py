"""The loadout: which skill sits in which slot, and which key casts it."""

import pygame

from app import config
from app.skills.abilities import Dash, Shield, WallSkill
from app.skills.base import Skill
from app.skills.utility import Blink, Sprint

# Slot order = order in the ability bar = order of the matching keys in config.
ABILITIES: tuple[type[Skill], ...] = (Shield, WallSkill, Dash)
UTILITY_SPELLS: tuple[type[Skill], ...] = (Sprint, Blink)


class SkillSlot:
    """One box in the ability bar: a key bound to a skill."""

    def __init__(self, key_name: str, skill: Skill) -> None:
        self.key_name = key_name
        self.key = pygame.key.key_code(key_name)    # "q" -> pygame.K_q
        self.skill = skill

    @property
    def key_label(self) -> str:
        return self.key_name.upper()


def build_loadout() -> list[SkillSlot]:
    """Fresh skills (all ready) for a new run: abilities first, then utility spells."""
    pairs = [*zip(config.ABILITY_KEYS, ABILITIES), *zip(config.UTILITY_KEYS, UTILITY_SPELLS)]
    return [SkillSlot(key, cls()) for key, cls in pairs]
