"""The in-game guide: every threat, skill, power-up and upgrade, in one scrolling page."""

import pygame

from app import config
from app.render.shapes import draw_panel
from app.render.text import draw_text
from app.scenes.base import Scene, dim
from app.theme.palette import PALETTE
from app.ui.document import Document
from app.ui.guide_content import build_guide
from app.ui.scroll import ScrollView
from app.ui.widgets import Button, ButtonGroup

LEFT = 46
SIDEBAR_W = 200
PANEL_TOP = 110
TEXT_PAD = 24           # px between the panel edge and the text
BAR_SPACE = 20          # px kept free on the right for the scrollbar


class GuideScene(Scene):
    """A sidebar of sections and the guide document in a scroll view.

    The sidebar highlights the section you are reading (it follows the
    scrolling) and jumps to a section when chosen. ``back`` is the scene to
    return to.
    """

    def __init__(self, game, back: Scene) -> None:
        super().__init__(game)
        self.back = back
        bottom = config.SCREEN_HEIGHT - 26
        self.panel = pygame.Rect(LEFT + SIDEBAR_W + 20, PANEL_TOP,
                                 config.SCREEN_WIDTH - LEFT * 2 - SIDEBAR_W - 20, bottom - PANEL_TOP)
        self.view = self.panel.inflate(0, -8)
        sections = build_guide(game.settings)
        self.document = Document(sections, self.panel.width - TEXT_PAD * 2 - BAR_SPACE)

        # Extra room at the bottom so even the last section can scroll up to the top.
        last_section = self.document.height - self.document.anchors[-1]
        padding = max(TEXT_PAD, self.view.height - last_section - TEXT_PAD)
        self.scroll = ScrollView(self.view, self.document.height + TEXT_PAD + padding)

        self.section_buttons: list[Button] = []
        for i, section in enumerate(sections):
            button = Button(section.title, self._jump(i), size=(SIDEBAR_W, 40))
            button.rect.topleft = (LEFT, PANEL_TOP + i * 48)
            self.section_buttons.append(button)
        back_button = Button("Back", self.go_back, hotkey="escape", size=(SIDEBAR_W, 44))
        back_button.rect.bottomleft = (LEFT, bottom)
        self.group = ButtonGroup(self.section_buttons + [back_button])

    def _jump(self, index: int):
        def jump() -> None:
            self.scroll.scroll_to(self.document.anchors[index])
        return jump

    @property
    def current_section(self) -> int:
        """The last section whose heading has reached the top of the view."""
        current = 0
        for i, anchor in enumerate(self.document.anchors):
            if anchor <= self.scroll.offset + 4:
                current = i
        return current

    def go_back(self) -> None:
        self.game.scene = self.back

    # --- Scene -------------------------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.scroll.handle_event(event):
            self.group.handle_event(event)

    def update(self, dt: float) -> None:
        self.scroll.update(dt)
        current = self.current_section
        for i, button in enumerate(self.section_buttons):
            button.primary = i == current
        self.group.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE.background)
        surface.blit(self.game.background, (0, 0))
        dim(surface, 120)
        draw_text(surface, "HOW TO PLAY", "heading", PALETTE.text, shadow=True, topleft=(LEFT, 26))
        draw_text(surface, "Scroll with the mouse wheel, the scrollbar, or Page Up / Page Down.", "small",
                  PALETTE.text_dim, topleft=(LEFT, 76))
        self.group.draw(surface)
        draw_panel(surface, self.panel, "frame")
        top = self.view.y + TEXT_PAD - self.scroll.offset
        self.document.draw(surface, self.panel.x + TEXT_PAD, top, self.view)
        self.scroll.draw_scrollbar(surface)
