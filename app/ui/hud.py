"""The in-game HUD.

Layout:
    top center      timer pill, danger bar
    top right       coins picked up this run
    top left        frame rate, if "Show frame rate" is on
    bottom center   ability bar (abilities | utility spells | power-up), key labels under the boxes
    left of bar     active effects (stasis, shield, sprint ...) with the time they have left
    right of bar    Second Wind, if owned: ready, or recharging
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from app import config
from app.render.icons import draw_icon
from app.render.shapes import (draw_bar, draw_cooldown_sweep, draw_glow, draw_panel,
                               draw_progress_ring)
from app.render.text import draw_keycap, draw_text
from app.skills.loadout import SkillSlot
from app.theme.accessibility import A11Y
from app.theme.palette import PALETTE, danger_color
from app.theme.styles import (HUD_BAR_PAD, HUD_BUFF_RADIUS, HUD_GROUP_GAP, HUD_KEYCAP_SPACE, HUD_MARGIN,
                              HUD_SLOT, HUD_SLOT_GAP, PANEL_STYLES)
from app.util.mathx import Color, clamp, lerp_color
from app.util.timefmt import fmt_time

if TYPE_CHECKING:                       # the HUD only reads a World; it never creates one
    from app.core.world import World


class Hud:
    """Draws the HUD for a World. Holds no game state of its own."""

    def draw(self, surface: pygame.Surface, world: World, fps: float | None = None) -> None:
        self.draw_timer(surface, world)
        self.draw_coins(surface, world)
        if fps is not None:
            draw_text(surface, f"{fps:.0f} FPS", "label", PALETTE.text_faint, shadow=True,
                      topleft=(HUD_MARGIN + 4, HUD_MARGIN + 4))
        slots = [*world.loadout, world.powerup_slot]
        groups = self.slot_groups(world)
        bar, rects = self.bar_layout(groups)
        draw_panel(surface, bar, "frame")
        for i, (slot, rect) in enumerate(zip(slots, rects)):
            if i and groups[i] != groups[i - 1]:
                x = rect.x - (HUD_GROUP_GAP + HUD_SLOT_GAP) // 2
                pygame.draw.line(surface, PALETTE.line, (x, rect.y + 8), (x, rect.bottom - 8))
            if slot.skill is None:
                self.draw_empty_slot(surface, slot, rect)
            else:
                self.draw_slot(surface, world, slot, rect)
        self.draw_buffs(surface, world, bar)
        if world.second_wind:
            self.draw_second_wind(surface, world, bar)

    # --- Timer and danger -----------------------------------------------------------------
    def draw_timer(self, surface: pygame.Surface, world: World) -> None:
        cx = config.SCREEN_WIDTH // 2
        pill = pygame.Rect(0, 0, 196, 44)
        pill.midtop = (cx, HUD_MARGIN)
        draw_panel(surface, pill, "chip")
        draw_text(surface, fmt_time(world.survival_time), "timer", PALETTE.text, shadow=True, center=pill.center)

        danger = world.danger
        color = danger_color(danger)
        if danger >= 1:
            # At max danger the bar pulses between red and white (a steady mix with reduced flashing).
            pulse = 0.0 if A11Y.reduce_flashing else math.sin(world.survival_time * 7)
            color = lerp_color(PALETTE.danger, PALETTE.text, 0.3 + 0.3 * pulse)
        bar = pygame.Rect(0, 0, pill.width, 6)
        bar.midtop = (cx, pill.bottom + 8)
        draw_bar(surface, bar, danger, color)
        label = "DANGER MAX" if danger >= 1 else f"DANGER {int(danger * 100)}%"
        draw_text(surface, label, "label", color, shadow=True, midtop=(cx, bar.bottom + 4))

    def draw_coins(self, surface: pygame.Surface, world: World) -> None:
        chip = pygame.Rect(0, 0, 96, 36)
        chip.topright = (config.SCREEN_WIDTH - HUD_MARGIN, HUD_MARGIN)
        draw_panel(surface, chip, "chip")
        draw_icon(surface, "coin", (chip.x + 20, chip.centery), 20, PALETTE.coin)
        draw_text(surface, str(world.coins_picked), "cooldown", PALETTE.coin, shadow=True,
                  midleft=(chip.x + 36, chip.centery))

    # --- Ability bar -----------------------------------------------------------------------
    @staticmethod
    def slot_groups(world: World) -> list[int]:
        """Group of each box, in bar order: 0 = abilities, 1 = utility spells, 2 = power-up."""
        return [1 if slot.skill.is_utility else 0 for slot in world.loadout] + [2]

    def bar_layout(self, groups: list[int]) -> tuple[pygame.Rect, list[pygame.Rect]]:
        """The frame around the bar and one rect per box, centered at the bottom.
        A wider gap separates the groups."""
        xs, x = [], 0
        for i in range(len(groups)):
            if i:
                x += HUD_SLOT_GAP + (HUD_GROUP_GAP if groups[i] != groups[i - 1] else 0)
            xs.append(x)
            x += HUD_SLOT
        bar = pygame.Rect(0, 0, x + HUD_BAR_PAD * 2, HUD_SLOT + HUD_BAR_PAD + HUD_KEYCAP_SPACE)
        bar.midbottom = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - HUD_MARGIN)
        rects = [pygame.Rect(bar.x + HUD_BAR_PAD + sx, bar.y + HUD_BAR_PAD, HUD_SLOT, HUD_SLOT) for sx in xs]
        return bar, rects

    def draw_slot(self, surface: pygame.Surface, world: World, slot: SkillSlot, rect: pygame.Rect) -> None:
        skill = slot.skill
        radius = PANEL_STYLES["slot"].radius
        draw_panel(surface, rect, "slot")
        if skill.ready:
            draw_glow(surface, skill.color, rect.center, 26, 60)
            icon_color = skill.color
        else:
            icon_color = lerp_color(skill.color, PALETTE.text_faint, 0.65)
        draw_icon(surface, skill.icon, (rect.centerx, rect.centery - 2), 30, icon_color)

        if not skill.ready:
            draw_cooldown_sweep(surface, rect, skill.cooldown_fraction, radius)
            seconds = skill.remaining
            text = f"{math.ceil(seconds)}" if seconds >= 1 else f"{seconds:0.1f}"
            draw_text(surface, text, "cooldown", PALETTE.text, shadow=True, center=rect.center)

        # While the effect lasts: an outer outline and a draining strip along the bottom.
        active = clamp(skill.active_fraction(world), 0.0, 1.0)
        if active > 0:
            pygame.draw.rect(surface, lerp_color(skill.color, PALETTE.panel_bottom, 0.45), rect.inflate(6, 6), 2,
                             border_radius=radius + 3)
            pygame.draw.rect(surface, skill.color, (rect.x + 5, rect.bottom - 7, round((rect.width - 10) * active), 3),
                             border_radius=2)

        pygame.draw.rect(surface, skill.color if skill.ready else PALETTE.line, rect,
                         2 if skill.ready else 1, border_radius=radius)
        if skill.ready_flash > 0:
            # Just came off cooldown: a bright outline grows out and fades.
            f = skill.ready_flash
            grow = int(10 * (1 - f))
            pygame.draw.rect(surface, lerp_color(PALETTE.panel_bottom, PALETTE.text, f),
                             rect.inflate(grow * 2, grow * 2), 2, border_radius=radius + grow)
        draw_keycap(surface, slot.key_label, midtop=(rect.centerx, rect.bottom - 8))

    @staticmethod
    def draw_empty_slot(surface: pygame.Surface, slot: SkillSlot, rect: pygame.Rect) -> None:
        """The power-up box with nothing held: a faint dashed diamond."""
        draw_panel(surface, rect, "slot")
        draw_icon(surface, "empty", (rect.centerx, rect.centery - 2), 30, PALETTE.text_faint)
        pygame.draw.rect(surface, PALETTE.line, rect, 1, border_radius=PANEL_STYLES["slot"].radius)
        draw_keycap(surface, slot.key_label, midtop=(rect.centerx, rect.bottom - 8))

    # --- Second Wind ---------------------------------------------------------------------------
    def draw_second_wind(self, surface: pygame.Surface, world: World, bar: pygame.Rect) -> None:
        """A badge right of the bar: bright when ready, a filling ring while it recharges."""
        skill = world.second_wind
        r = HUD_BUFF_RADIUS
        x, cy = bar.right + 16 + r, bar.centery - 6
        pygame.draw.circle(surface, PALETTE.panel_bottom, (x, cy), r)
        if skill.ready:
            draw_glow(surface, skill.color, (x, cy), r * 1.6, 70)
            pygame.draw.circle(surface, skill.color, (x, cy), r, 2)
            draw_icon(surface, skill.icon, (x, cy), 22, skill.color)
            label, label_color = "READY", skill.color
        else:
            pygame.draw.circle(surface, PALETTE.line, (x, cy), r, 1)
            draw_progress_ring(surface, (x, cy), r, 1 - skill.cooldown_fraction, skill.color, 3)
            draw_icon(surface, skill.icon, (x, cy), 22, lerp_color(skill.color, PALETTE.text_faint, 0.65))
            label, label_color = f"{math.ceil(skill.remaining)}s", PALETTE.text_dim
        if skill.ready_flash > 0:
            grow = int(10 * (1 - skill.ready_flash))
            pygame.draw.circle(surface, lerp_color(PALETTE.panel_bottom, PALETTE.text, skill.ready_flash),
                               (x, cy), r + grow, 2)
        draw_text(surface, label, "tiny", label_color, shadow=True, midtop=(x, cy + r + 4))

    # --- Active effects ----------------------------------------------------------------------
    @staticmethod
    def buff_list(world: World) -> list[tuple[str, Color, float, float]]:
        """(icon, color, fraction left, seconds left) for each active effect."""
        p = world.player
        buffs = []
        if p.in_stasis:
            buffs.append(("stasis", PALETTE.stasis, p.stasis_remaining / config.STASIS_DURATION, p.stasis_remaining))
        if p.invulnerable_remaining > 0:
            buffs.append(("second_wind", PALETTE.second_wind,
                          p.invulnerable_remaining / config.SECOND_WIND_INVULN_TIME, p.invulnerable_remaining))
        if world.time_warped:
            buffs.append(("time_warp", PALETTE.time_warp,
                          world.time_warp_remaining / config.TIME_WARP_DURATION, world.time_warp_remaining))
        if world.coin_rush:
            buffs.append(("coin_rush", PALETTE.coin,
                          world.coin_rush_remaining / config.COIN_RUSH_DURATION, world.coin_rush_remaining))
        if p.shielded:
            buffs.append(("shield", PALETTE.shield, p.shield_remaining / p.shield_duration, p.shield_remaining))
        sprint = p.speed_buffs.get("sprint")
        if sprint:
            buffs.append(("sprint", PALETTE.sprint, sprint.remaining / sprint.duration, sprint.remaining))
        return buffs

    def draw_buffs(self, surface: pygame.Surface, world: World, bar: pygame.Rect) -> None:
        r = HUD_BUFF_RADIUS
        x, cy = bar.left - 16 - r, bar.centery - 6
        for icon, color, fraction, seconds in self.buff_list(world):
            pygame.draw.circle(surface, PALETTE.panel_bottom, (x, cy), r)
            pygame.draw.circle(surface, PALETTE.line, (x, cy), r, 1)
            draw_progress_ring(surface, (x, cy), r, fraction, color, 3)
            draw_icon(surface, icon, (x, cy), 20, color)
            draw_text(surface, f"{seconds:0.1f}", "tiny", PALETTE.text_dim, shadow=True, midtop=(x, cy + r + 4))
            x -= 2 * r + 10
