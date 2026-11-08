"""The settings screen: a card with tabs for controls, gameplay and accessibility."""

import pygame

from app.core.settings import ACTION_LABELS, MOVE_BUTTONS
from app.render.icons import draw_icon
from app.render.shapes import draw_panel
from app.render.text import draw_keycap, draw_text, line_height, wrap_text
from app.scenes.base import Scene, card_rect, dim, draw_card
from app.theme.palette import PALETTE
from app.ui.widgets import Button, ButtonGroup, ChoiceRow, ColorRow, KeyBindRow, TabButton, ToggleRow
from app.util.keys import is_valid_key_name

CARD_W, CARD_H = 780, 660
PAD = 28
ROW_H, ROW_GAP = 40, 8
CONFIRM_TIME = 3.0          # s to click "Reset to defaults" a second time
TABS = ("Controls", "Gameplay", "Accessibility")

COLOR_MODE_LABELS = {"default": "Default", "deuteranopia": "Deuteranopia", "protanopia": "Protanopia",
                     "tritanopia": "Tritanopia", "high_contrast": "High contrast"}
COLOR_MODE_DESCRIPTIONS = {
    "default": "The standard colors.",
    "deuteranopia": "Red-green (green-weak). Bolts turn orange, lasers yellow, you stay blue.",
    "protanopia": "Red-green (red-weak). Brighter orange bolts that don't fade into the dark.",
    "tritanopia": "Blue-yellow. Red bolts, a teal player, white lasers and orange coins.",
    "high_contrast": "A pure black arena, strong colors, and outlines on every threat.",
}
ASSIST_NOTE = "Applies from your next run. Below 100%, runs don't count for best times."


class SettingsScene(Scene):
    """Every change is saved immediately. ``back`` is the scene to return to.

    Rebinding: activate a key row, then press the new key (Esc cancels). A key
    already used by another action swaps with it. Left / Right change the
    focused choice, or switch tabs while a tab is focused.
    """

    def __init__(self, game, back: Scene) -> None:
        super().__init__(game)
        self.back = back
        self.waiting_for: str | None = None        # the action waiting for a new key
        self.confirm_timer = 0.0
        self.tab = 0
        self.card = card_rect(CARD_W, CARD_H)
        inner = self.card.width - PAD * 2

        tab_w = inner // len(TABS)
        self.tabs = []
        for i, name in enumerate(TABS):
            tab = TabButton(name, self._open_tab(i), self._is_open(i), size=(tab_w, 36))
            tab.rect.topleft = (self.card.x + PAD + i * tab_w, self.card.y + 82)
            self.tabs.append(tab)
        self.rows_top = self.card.y + 134

        self.back_button = Button("Back", self.go_back, hotkey="escape", primary=True, size=(200, 44))
        self.back_button.rect.bottomright = (self.card.right - PAD, self.card.bottom - 24)
        self.reset_button = Button(lambda: "Click again to confirm" if self.confirm_timer > 0 else "Reset to defaults",
                                   self.reset, size=(250, 44))
        self.reset_button.rect.bottomleft = (self.card.x + PAD, self.card.bottom - 24)
        self.rows: list[Button] = []
        self.build_tab()

    # --- Tabs --------------------------------------------------------------------------------------
    def _open_tab(self, index: int):
        def open_tab() -> None:
            self.tab = index
            self.build_tab()
        return open_tab

    def _is_open(self, index: int):
        return lambda: self.tab == index

    def build_tab(self) -> None:
        """Create the rows of the open tab and a fresh focus group, focused on the tab itself."""
        size = (self.card.width - PAD * 2, ROW_H)
        self.rows = (self.control_rows, self.gameplay_rows, self.accessibility_rows)[self.tab](size)
        for i, row in enumerate(self.rows):
            row.rect.topleft = (self.card.x + PAD, self.rows_top + i * (ROW_H + ROW_GAP))
        self.group = ButtonGroup(self.tabs + self.rows + [self.reset_button, self.back_button])
        self.group.focus = self.tab

    def control_rows(self, size) -> list[Button]:
        s = self.game.settings
        rows: list[Button] = [KeyBindRow(label, self._listen(action), self._key_of(action),
                                         self._is_waiting(action), size,
                                         "Choose the row, then press the new key. Esc cancels.")
                              for action, label in ACTION_LABELS.items()]
        rows.append(ChoiceRow("Move with", s.cycle_move_button, lambda: MOVE_BUTTONS[s.move_button], size,
                              "The mouse button that walks and follows the cursor."))
        return rows

    def gameplay_rows(self, size) -> list[Button]:
        o = self.game.settings.options
        return [
            ToggleRow("Pause when the window loses focus", self._toggle("pause_on_focus_loss"),
                      lambda: o["pause_on_focus_loss"], size, "Alt-tab away and the run waits for you."),
            ToggleRow("Show frame rate", self._toggle("show_fps"), lambda: o["show_fps"], size,
                      "Frames per second in the top-left corner during a run."),
            ChoiceRow("Starting danger", self._cycle("start_danger"), lambda: f"{o['start_danger']}%", size,
                      "Start a run further up the danger ramp, for practice at higher speeds. "
                      "Applies from your next run."),
            ChoiceRow("Game speed", self._cycle("game_speed"), lambda: f"{o['game_speed']}%", size,
                      "Slows the whole run down. " + ASSIST_NOTE),
            ChoiceRow("Laser warning time", self._cycle("laser_warning"), lambda: f"{o['laser_warning']}%", size,
                      "Lasers warn you longer before they fire. " + ASSIST_NOTE),
        ]

    def accessibility_rows(self, size) -> list[Button]:
        o = self.game.settings.options
        return [
            ChoiceRow("Color mode", self._cycle("color_mode"), lambda: COLOR_MODE_LABELS[o["color_mode"]], size,
                      "Palettes for color vision deficiency. The preview below shows the result."),
            ColorRow("Player color", self._cycle("color_player"), lambda: o["color_player"],
                     lambda: PALETTE.player, size, "Your own color. Auto follows the color mode."),
            ColorRow("Bolt color", self._cycle("color_bolt"), lambda: o["color_bolt"],
                     lambda: PALETTE.bolt, size, "The color of bolts. Auto follows the color mode."),
            ColorRow("Laser color", self._cycle("color_laser"), lambda: o["color_laser"],
                     lambda: PALETTE.laser, size, "The color of lasers. Auto follows the color mode."),
            ToggleRow("Threat outlines", self._toggle("threat_outlines"), lambda: o["threat_outlines"], size,
                      "A bright outline around every bolt and laser. Always on in High contrast."),
            ToggleRow("Reduce flashing", self._toggle("reduce_flashing"), lambda: o["reduce_flashing"], size,
                      "Nothing blinks or pulses: things about to vanish stay steady instead."),
            ToggleRow("Reduced motion", self._toggle("reduced_motion"), lambda: o["reduced_motion"], size,
                      "No floating, wobbling, spinning, sliding or smooth scrolling."),
        ]

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

    def _cycle(self, option: str):
        return lambda step: self.game.settings.cycle(option, step)

    def reset(self) -> None:
        if self.confirm_timer <= 0:
            self.confirm_timer = CONFIRM_TIME
            return
        self.confirm_timer = 0
        self.game.settings.reset()

    def go_back(self) -> None:
        self.game.scene = self.back

    @property
    def focused(self) -> Button:
        return self.group.buttons[self.group.focus]

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
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = 1 if event.key == pygame.K_RIGHT else -1
            if isinstance(self.focused, ChoiceRow):
                self.focused.change(step)
                return
            if isinstance(self.focused, TabButton):
                self._open_tab((self.tab + step) % len(TABS))()
                return
        self.group.handle_event(event)

    def update(self, dt: float) -> None:
        self.confirm_timer = max(0.0, self.confirm_timer - dt)
        self.group.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE.background)
        surface.blit(self.game.background, (0, 0))
        dim(surface, 120)
        draw_card(surface, self.card)
        card = self.card
        draw_text(surface, "SETTINGS", "heading", PALETTE.text, shadow=True, topleft=(card.x + PAD, card.y + 22))
        draw_text(surface, "Changes are saved right away.", "small", PALETTE.text_faint,
                  bottomright=(card.right - PAD, card.y + 60))
        pygame.draw.line(surface, PALETTE.line, (card.x + PAD, card.y + 118), (card.right - PAD, card.y + 118))
        self.group.draw(surface)
        if TABS[self.tab] == "Accessibility":
            self.draw_preview(surface)
        self.draw_description(surface)
        self.draw_key_hints(surface)

    def draw_description(self, surface: pygame.Surface) -> None:
        """The focused row's explanation (or the color mode's), just above the bottom buttons."""
        row = self.focused
        text = getattr(row, "desc", "")
        if row is self.rows[0] and TABS[self.tab] == "Accessibility":
            text = COLOR_MODE_DESCRIPTIONS[self.game.settings.options["color_mode"]]
        y = self.card.bottom - 24 - 44 - 14 - 2 * line_height("small")
        for line in wrap_text(text, "small", self.card.width - PAD * 2)[:2]:
            draw_text(surface, line, "small", PALETTE.text_dim, topleft=(self.card.x + PAD, y))
            y += line_height("small")

    def draw_key_hints(self, surface: pygame.Surface) -> None:
        x = self.reset_button.rect.right + 18
        y = self.reset_button.rect.centery
        for keys, label in ((("ARROWS",), "Move"), (("ENTER",), "Change")):
            for key in keys:
                x = draw_keycap(surface, key, midleft=(x, y)).right + 6
            x = draw_text(surface, label, "tiny", PALETTE.text_faint, midleft=(x, y)).right + 14

    def draw_preview(self, surface: pygame.Surface) -> None:
        """A strip showing the main colors as they look right now."""
        top = self.rows_top + len(self.rows) * (ROW_H + ROW_GAP)
        strip = pygame.Rect(self.card.x + PAD, top, self.card.width - PAD * 2, 44)
        draw_panel(surface, strip, "slot")
        draw_text(surface, "PREVIEW", "label", PALETTE.text_faint, midleft=(strip.x + 14, strip.centery))
        items = (("Player", None, PALETTE.player), ("Bolt", "bolt", PALETTE.bolt), ("Laser", "laser", PALETTE.laser),
                 ("Coin", "coin", PALETTE.coin), ("Shield", "shield", PALETTE.shield), ("Wall", "wall", PALETTE.wall))
        x = strip.x + 100
        for name, icon, color in items:
            if icon:
                draw_icon(surface, icon, (x, strip.centery), 22, color)
            else:
                pygame.draw.circle(surface, color, (x, strip.centery), 9)
                pygame.draw.circle(surface, PALETTE.player_outline, (x, strip.centery), 9, 2)
            x = draw_text(surface, name, "small", PALETTE.text_dim, midleft=(x + 16, strip.centery)).right + 26
