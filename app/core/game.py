"""The Game: owns the window, the main loop and the current run."""

import pygame

from app import config
from app.core.world import World
from app.entities.laser import Laser
from app.meta import APP_NAME
from app.render.arena import build_arena_background
from app.render.text import draw_text
from app.theme.palette import PALETTE, danger_color
from app.util.mathx import lerp_color


class Game:
    """Creates the window and runs a frame-rate independent main loop.

    Each frame: handle input -> update the simulation by ``dt`` seconds -> draw.
    A run lives in a ``World``; restarting just creates a new one.
    """

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        self.clock = pygame.time.Clock()
        self.background = build_arena_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))
        self.world = World()
        self.running = True

    # --- Main loop ----------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            # Clamp dt so a stall (e.g. dragging the window) can't make things jump.
            dt = min(self.clock.tick(config.FPS) / 1000.0, config.MAX_FRAME_DT)
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.world.over:
                    self.world = World()                      # restart
                else:
                    for index, slot in enumerate(self.world.loadout):
                        if event.key == slot.key:
                            self.world.cast(index, pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == config.MOVE_MOUSE_BUTTON:
                if not self.world.over:
                    self.world.command_move(event.pos, new_click=True)

    def update(self, dt: float) -> None:
        # Holding the move button keeps updating the destination.
        if not self.world.over and pygame.mouse.get_pressed()[config.MOVE_MOUSE_BUTTON - 1]:
            self.world.command_move(pygame.mouse.get_pos(), new_click=False)
        self.world.update(dt)

    # --- Drawing ------------------------------------------------------------------------
    def draw(self) -> None:
        self.screen.fill(PALETTE.background)
        self.screen.blit(self.background, (0, 0))
        self.world.draw(self.screen)
        self.draw_hud()
        if self.world.over:
            self.draw_game_over()

    def draw_hud(self) -> None:
        """Survival timer with the danger bar underneath."""
        cx = config.SCREEN_WIDTH // 2
        timer = draw_text(self.screen, f"{self.world.survival_time:0.1f}s", 32, PALETTE.text, bold=True,
                          midtop=(cx, 14))
        danger = self.world.danger
        color = danger_color(danger)
        bar = pygame.Rect(0, 0, 180, 6)
        bar.midtop = (cx, timer.bottom + 6)
        pygame.draw.rect(self.screen, PALETTE.track, bar, border_radius=3)
        filled = int(bar.width * danger)
        if filled > 0:
            pygame.draw.rect(self.screen, color, (bar.x, bar.y, max(filled, bar.height), bar.height),
                             border_radius=3)
        label = "DANGER MAX" if danger >= 1 else f"DANGER {int(danger * 100)}%"
        draw_text(self.screen, label, 14, color, bold=True, midtop=(cx, bar.bottom + 4))
        self.draw_ability_bar()

    def draw_ability_bar(self) -> None:
        """One box per skill at the bottom: key, name, and a cooldown that refills from the bottom."""
        size, gap, group_gap = 64, 12, 32       # a wider gap separates abilities from utility spells
        slots = self.world.loadout
        groups = sum(1 for a, b in zip(slots, slots[1:]) if a.skill.is_utility != b.skill.is_utility)
        total = len(slots) * size + (len(slots) - 1) * gap + groups * (group_gap - gap)
        x = (config.SCREEN_WIDTH - total) // 2
        y = config.SCREEN_HEIGHT - size - 18
        previous = None
        for slot in slots:
            skill = slot.skill
            if previous is not None and previous.is_utility != skill.is_utility:
                x += group_gap - gap
            previous = skill
            box = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, PALETTE.track, box, border_radius=10)
            if skill.ready:
                pygame.draw.rect(self.screen, skill.color, box, 2, border_radius=10)
                draw_text(self.screen, skill.name, 15, skill.color, bold=True, center=box.center)
            else:
                # The tinted part is the cooldown already recovered; it fills up until ready.
                # Drawn as a full rounded box with its top erased, so it keeps the box's corners.
                filled = int(size * (1 - skill.cooldown_fraction))
                if filled > 0:
                    tile = pygame.Surface(box.size, pygame.SRCALPHA)
                    pygame.draw.rect(tile, lerp_color(PALETTE.track, skill.color, 0.35), tile.get_rect(),
                                     border_radius=10)
                    tile.fill((0, 0, 0, 0), (0, 0, size, size - filled))
                    self.screen.blit(tile, box)
                pygame.draw.rect(self.screen, PALETTE.border, box, 2, border_radius=10)
                draw_text(self.screen, f"{skill.remaining:0.1f}", 20, PALETTE.text, bold=True, center=box.center)
            draw_text(self.screen, slot.key_label, 13, PALETTE.text_dim, bold=True, topleft=(box.x + 6, box.y + 4))
            x += size + gap

    def draw_game_over(self) -> None:
        self.screen.blit(self.overlay, (0, 0))
        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        cause = "a laser" if isinstance(self.world.killer, Laser) else "a bolt"
        draw_text(self.screen, "GAME OVER", 64, PALETTE.danger, bold=True, center=(cx, cy - 70))
        draw_text(self.screen, f"You survived {self.world.survival_time:0.2f} seconds (hit by {cause})", 26,
                  PALETTE.text, center=(cx, cy))
        draw_text(self.screen, "Press R to restart   |   Esc to quit", 22, PALETTE.text_dim,
                  center=(cx, cy + 60))
