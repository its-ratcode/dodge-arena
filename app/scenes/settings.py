"""The settings screen: key bindings, the move button, and on/off options."""

import pygame

from app import config
from app.core.settings import ACTION_LABELS, MOVE_BUTTONS
from app.render.text import draw_text
from app.scenes.base import Scene, dim
from app.theme.palette import PALETTE
from app.ui.widgets import Button, ButtonGroup, KeyBindRow, SettingRow, ToggleRow
from app.util.keys import is_valid_key_name

COLUMN_W = 480
ROW_H, ROW_GAP = 42, 8
TOP = 150
CONFIRM_TIME = 3.0          # s to click "Reset to defaults" a second time

OPTION_LABELS = {
    "pause_on_focus_loss": "Pause when the window loses focus",
    "show_fps": "Show frame rate",
}


class SettingsScene(Scene):
    """Every change is saved immediately. ``back`` is the scene to return to.

    Rebinding: activate a key row, then press the new key (Esc cancels). A key
    already used by another action swaps with it.
    """

    def __init__(self, game, back: Scene) -> None:
        super().__init__(game)
        self.back = back
        self.waiting_for: str | None = None        # the action waiting for a new key
        self.confirm_timer = 0.0
        settings = game.settings
        gap = config.SCREEN_WIDTH - 2 * COLUMN_W
        self.left = gap // 3
        self.right = self.left * 2 + COLUMN_W

        rows: list[Button] = []
        y = TOP
        for action, label in ACTION_LABELS.items():
            row = KeyBindRow(label, self._listen(action), self._key_of(action),
                             self._is_waiting(action), size=(COLUMN_W, ROW_H))
            row.rect.topleft = (self.left, y)
            rows.append(row)
            y += ROW_H + ROW_GAP
        move = SettingRow("Move", settings.cycle_move_button, lambda: MOVE_BUTTONS[settings.move_button],
                          size=(COLUMN_W, ROW_H))
        move.rect.topleft = (self.left, y)
        rows.append(move)

        y = TOP
        for option, label in OPTION_LABELS.items():
            toggle = ToggleRow(label, self._toggle(option), self._option(option), size=(COLUMN_W, ROW_H))
            toggle.rect.topleft = (self.right, y)
            rows.append(toggle)
            y += ROW_H + ROW_GAP

        bottom = config.SCREEN_HEIGHT - 26
        back_button = Button("Back", self.go_back, hotkey="escape", size=(200, 44))
        back_button.rect.bottomleft = (self.left, bottom)
        reset = Button(lambda: "Click again to confirm" if self.confirm_timer > 0 else "Reset to defaults",
                       self.reset, size=(260, 44))
        reset.rect.bottomright = (self.right + COLUMN_W, bottom)
        self.group = ButtonGroup(rows + [back_button, reset])

    # --- Row callbacks (each returns a function bound to one action or option) --------------------
    def _listen(self, action: str):
        def listen() -> None:
            self.waiting_for = action
        return listen

    def _key_of(self, action: str):
        return lambda: self.game.settings.keybinds[action]

    def _is_waiting(self, action: str):
        return lambda: self.waiting_for == action

    def _toggle(self, option: str):
        return lambda: self.game.settings.toggle(option)

    def _option(self, option: str):
        return lambda: self.game.settings.options[option]

    def reset(self) -> None:
        if self.confirm_timer <= 0:
            self.confirm_timer = CONFIRM_TIME
            return
        self.confirm_timer = 0
        self.game.settings.reset()

    def go_back(self) -> None:
        self.game.scene = self.back

    # --- Scene -------------------------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.waiting_for:
            # Waiting for a key: the next key press is the new binding; Esc or a click cancels.
            if event.type == pygame.KEYDOWN:
                name = pygame.key.name(event.key)
                if event.key != pygame.K_ESCAPE and is_valid_key_name(name):     # unknown keys are ignored
                    self.game.settings.bind(self.waiting_for, name)
                self.waiting_for = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.waiting_for = None
            return
        self.group.handle_event(event)

    def update(self, dt: float) -> None:
        self.confirm_timer = max(0.0, self.confirm_timer - dt)
        self.group.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE.background)
        surface.blit(self.game.background, (0, 0))
        dim(surface, 120)
        draw_text(surface, "SETTINGS", "heading", PALETTE.text, shadow=True, topleft=(self.left, 26))
        draw_text(surface, "Changes are saved right away.", "small", PALETTE.text_dim, topleft=(self.left, 76))
        draw_text(surface, "CONTROLS", "label", PALETTE.text_faint, topleft=(self.left, TOP - 22))
        draw_text(surface, "OPTIONS", "label", PALETTE.text_faint, topleft=(self.right, TOP - 22))
        self.group.draw(surface)
        hints = ("Click a control, then press the new key.",
                 "A key already in use swaps places with it.",
                 "Menus always use the mouse, arrows, Enter and Esc.")
        y = TOP + len(OPTION_LABELS) * (ROW_H + ROW_GAP) + 16
        for line in hints:
            draw_text(surface, line, "small", PALETTE.text_faint, topleft=(self.right, y))
            y += 22
