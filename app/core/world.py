"""The World: everything that belongs to one run."""

import random

import pygame
from pygame.math import Vector2

from app import config
from app.core.difficulty import danger_level, ramp
from app.entities.bolt import Bolt
from app.entities.laser import Laser
from app.entities.player import Player
from app.render.effects import ClickMarker
from app.theme.palette import PALETTE

Threat = Bolt | Laser


class World:
    """One run: the player, the threats, the survival clock and the spawn timers.

    A new run is simply a new World. ``killer`` is set to whatever hit the
    player, which ends the run.
    """

    def __init__(self) -> None:
        self.player = Player((config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2))
        self.bolts: list[Bolt] = []
        self.lasers: list[Laser] = []
        self.marker: ClickMarker | None = None
        self.survival_time = 0.0
        self.spawn_timer = config.FIRST_SPAWN_DELAY
        self.laser_timer = config.LASER_FIRST_DELAY
        self.killer: Threat | None = None
        # Transparent layer for lasers (they need alpha); cleared and reused every frame.
        self.fx_layer = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)

    @property
    def over(self) -> bool:
        return self.killer is not None

    @property
    def danger(self) -> float:
        return danger_level(self.survival_time)

    # --- Input ---------------------------------------------------------------------------
    def command_move(self, pos, new_click: bool) -> None:
        """Send the player to ``pos``. A fresh click restarts the marker animation;
        while the button is held, the marker follows the cursor and re-pulses."""
        self.player.move_to(pos)
        if new_click or self.marker is None or not self.marker.alive:
            self.marker = ClickMarker(self.player.destination)
        else:
            self.marker.pos.update(self.player.destination)

    # --- Simulation ------------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.over:
            return
        self.survival_time += dt
        self.player.update(dt)
        if self.marker:
            self.marker.update(dt)

        self.update_spawning(dt)
        for bolt in self.bolts:
            bolt.update(dt)
        for laser in self.lasers:
            laser.update(dt)
        self.bolts = [b for b in self.bolts if not b.is_off_screen()]
        self.lasers = [laser for laser in self.lasers if laser.alive]
        self.check_hits()

    def update_spawning(self, dt: float) -> None:
        danger = self.danger
        # Bolts: a while-loop keeps the rate exact even on long frames.
        self.spawn_timer -= dt
        while self.spawn_timer <= 0:
            self.spawn_bolt()
            if random.random() < ramp(config.DOUBLE_SHOT_CHANCE_START, config.DOUBLE_SHOT_CHANCE_END, danger):
                self.spawn_bolt()                                   # second bolt from another edge
            self.spawn_timer += ramp(config.BOLT_SPAWN_INTERVAL_START, config.BOLT_SPAWN_INTERVAL_END, danger)
        # Lasers: random gaps that shrink as danger rises.
        self.laser_timer -= dt
        if self.laser_timer <= 0:
            self.spawn_laser()
            self.laser_timer = random.uniform(
                ramp(config.LASER_INTERVAL_MIN_START, config.LASER_INTERVAL_MIN_END, danger),
                ramp(config.LASER_INTERVAL_MAX_START, config.LASER_INTERVAL_MAX_END, danger))

    def check_hits(self) -> None:
        p = self.player
        for bolt in self.bolts:
            if bolt.shape.collides_circle(p.pos, p.radius):
                self.killer = bolt
                return
        for laser in self.lasers:
            if laser.firing and laser.shape.collides_circle(p.pos, p.radius):
                self.killer = laser
                return

    def spawn_bolt(self) -> None:
        """Spawn just outside a random edge, aimed at the player's current position."""
        offset = config.BOLT_LENGTH / 2 + config.BOLT_SPAWN_MARGIN
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        edge = random.choice(("top", "bottom", "left", "right"))
        if edge == "top":
            spawn = Vector2(random.uniform(0, w), -offset)
        elif edge == "bottom":
            spawn = Vector2(random.uniform(0, w), h + offset)
        elif edge == "left":
            spawn = Vector2(-offset, random.uniform(0, h))
        else:
            spawn = Vector2(w + offset, random.uniform(0, h))
        speed = ramp(config.BOLT_SPEED_START, config.BOLT_SPEED_END, self.danger)
        speed *= random.uniform(1 - config.BOLT_SPEED_VARIANCE, 1 + config.BOLT_SPEED_VARIANCE)
        self.bolts.append(Bolt(spawn, self.player.pos, speed))

    def spawn_laser(self) -> None:
        """Aim a beam through the player's current position from a random angle."""
        origin = self.player.pos + Vector2(1, 0).rotate(random.uniform(0, 360)) * 100
        warning = ramp(config.LASER_WARNING_START, config.LASER_WARNING_END, self.danger)
        self.lasers.append(Laser(origin, self.player.pos, warning))

    # --- Drawing -------------------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.marker and self.marker.alive and not self.over:
            self.marker.draw(surface)
        for bolt in self.bolts:
            bolt.draw(surface, highlight=bolt is self.killer)
        if self.lasers:
            self.fx_layer.fill((0, 0, 0, 0))
            for laser in self.lasers:
                laser.draw(self.fx_layer)
            surface.blit(self.fx_layer, (0, 0))
        self.player.draw(surface)
        if self.over:
            pygame.draw.circle(surface, PALETTE.danger, self.player.pos, self.player.radius + 6, 3)
