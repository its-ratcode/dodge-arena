"""The World: everything that belongs to one run."""

import random

import pygame
from pygame.math import Vector2

from app import config
from app.entities.bolt import Bolt
from app.entities.player import Player
from app.render.effects import ClickMarker
from app.theme.palette import PALETTE


class World:
    """One run: the player, the bolts, the survival clock and the spawn timer.

    A new run is simply a new World. ``killer`` is set to the bolt that hit the
    player, which ends the run.
    """

    def __init__(self) -> None:
        self.player = Player((config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2))
        self.bolts: list[Bolt] = []
        self.marker: ClickMarker | None = None
        self.survival_time = 0.0
        self.spawn_timer = config.FIRST_SPAWN_DELAY
        self.killer: Bolt | None = None

    @property
    def over(self) -> bool:
        return self.killer is not None

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

        # Fixed-rate spawning (a while-loop keeps the rate exact even on long frames).
        self.spawn_timer -= dt
        while self.spawn_timer <= 0:
            self.spawn_bolt()
            self.spawn_timer += config.BOLT_SPAWN_INTERVAL

        for bolt in self.bolts:
            bolt.update(dt)
        self.bolts = [b for b in self.bolts if not b.is_off_screen()]

        for bolt in self.bolts:
            if bolt.shape.collides_circle(self.player.pos, self.player.radius):
                self.killer = bolt
                break

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
        self.bolts.append(Bolt(spawn, self.player.pos))

    # --- Drawing -------------------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if self.marker and self.marker.alive and not self.over:
            self.marker.draw(surface)
        for bolt in self.bolts:
            bolt.draw(surface, highlight=bolt is self.killer)
        self.player.draw(surface)
        if self.over:
            pygame.draw.circle(surface, PALETTE.danger, self.player.pos, self.player.radius + 6, 3)
