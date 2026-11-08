"""A tiny document layout: blocks of text and cards stacked top to bottom.

Each block measures itself for a given width (``layout``), then draws at a
position (``draw``). The ``Document`` stacks them and only draws the blocks
that are inside the visible area, so long pages stay cheap.
"""

from dataclasses import dataclass, field

import pygame

from app.render.icons import draw_icon
from app.render.shapes import draw_panel
from app.render.text import draw_keycap, draw_text, line_height, text_size, wrap_text
from app.theme.palette import PALETTE
from app.theme.styles import RADIUS_SM

BLOCK_GAP = 14          # px between blocks
CARD_PAD = 16
ICON_AREA = 64          # px reserved on the left of an entry card for its icon badge
FACT_H, FACT_GAP = 26, 8


class Block:
    height = 0

    def layout(self, width: int) -> int:
        """Work out the height for ``width`` px, store it and return it."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        raise NotImplementedError


class Heading(Block):
    """A section title with an accent underline. Sections are what the sidebar jumps to."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.width = 0

    def layout(self, width: int) -> int:
        self.width = width
        self.height = line_height("timer") + 12
        return self.height

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        draw_text(surface, self.text, "timer", PALETTE.text, shadow=True, topleft=(x, y))
        bottom = y + self.height - 4
        pygame.draw.line(surface, PALETTE.line, (x, bottom), (x + self.width, bottom))
        pygame.draw.line(surface, PALETTE.accent, (x, bottom), (x + 60, bottom), 3)


class Paragraph(Block):
    def __init__(self, text: str, style: str = "body") -> None:
        self.text = text
        self.style = style
        self.lines: list[str] = []

    def layout(self, width: int) -> int:
        self.lines = wrap_text(self.text, self.style, width)
        self.height = len(self.lines) * line_height(self.style)
        return self.height

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        step = line_height(self.style)
        for i, line in enumerate(self.lines):
            draw_text(surface, line, self.style, PALETTE.text_dim, topleft=(x, y + i * step))


class Bullets(Block):
    """A list; long items wrap with a hanging indent."""

    INDENT = 20

    def __init__(self, items: list[str]) -> None:
        self.items = items
        self.wrapped: list[list[str]] = []

    def layout(self, width: int) -> int:
        self.wrapped = [wrap_text(item, "body", width - self.INDENT) for item in self.items]
        self.height = sum(len(lines) for lines in self.wrapped) * line_height("body") + 6 * (len(self.items) - 1)
        return self.height

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        step = line_height("body")
        for lines in self.wrapped:
            pygame.draw.circle(surface, PALETTE.accent, (x + 6, y + step // 2 + 1), 3)
            for line in lines:
                draw_text(surface, line, "body", PALETTE.text_dim, topleft=(x + self.INDENT, y))
                y += step
            y += 6


@dataclass
class Entry(Block):
    """A card for one thing in the game: icon badge, name, key, description and quick facts."""

    icon: str
    color_name: str                     # palette field, read at draw time
    title: str
    text: str
    key: str | None = None              # keycap label, e.g. "Q"
    facts: list[tuple[str, str]] = field(default_factory=list)    # ("COOLDOWN", "12 s")

    def __post_init__(self) -> None:
        self.lines: list[str] = []
        self.fact_rects: list[pygame.Rect] = []      # relative to the card's top-left
        self.width = 0

    @staticmethod
    def _fact_width(label: str, value: str) -> int:
        return text_size(label, "label")[0] + 8 + text_size(value, "small")[0] + 20

    def layout(self, width: int) -> int:
        self.width = width
        text_x = CARD_PAD + ICON_AREA
        text_w = width - text_x - CARD_PAD
        self.lines = wrap_text(self.text, "body", text_w)
        y = CARD_PAD + line_height("button") + 4 + len(self.lines) * line_height("body")
        # Facts flow left to right and wrap onto new rows.
        self.fact_rects = []
        if self.facts:
            y += 10
            fx = text_x
            for label, value in self.facts:
                w = self._fact_width(label, value)
                if fx + w > width - CARD_PAD and fx > text_x:
                    fx, y = text_x, y + FACT_H + FACT_GAP
                self.fact_rects.append(pygame.Rect(fx, y, w, FACT_H))
                fx += w + FACT_GAP
            y += FACT_H
        self.height = max(y, CARD_PAD + 52) + CARD_PAD
        return self.height

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        color = getattr(PALETTE, self.color_name)
        card = pygame.Rect(x, y, self.width, self.height)
        draw_panel(surface, card, "chip")
        pygame.draw.rect(surface, color, (card.x, card.y + 10, 3, card.height - 20), border_radius=2)   # color tab
        badge = (x + CARD_PAD + 26, y + CARD_PAD + 26)
        pygame.draw.circle(surface, PALETTE.panel_bottom, badge, 26)
        pygame.draw.circle(surface, color, badge, 26, 2)
        draw_icon(surface, self.icon, badge, 30, color)

        text_x = x + CARD_PAD + ICON_AREA
        title = draw_text(surface, self.title, "button", PALETTE.text, shadow=True, topleft=(text_x, y + CARD_PAD))
        if self.key:
            draw_keycap(surface, self.key, midleft=(title.right + 10, title.centery))
        ty = y + CARD_PAD + line_height("button") + 4
        for line in self.lines:
            draw_text(surface, line, "body", PALETTE.text_dim, topleft=(text_x, ty))
            ty += line_height("body")
        for (label, value), rect in zip(self.facts, self.fact_rects):
            r = rect.move(x, y)
            pygame.draw.rect(surface, PALETTE.panel_bottom, r, border_radius=RADIUS_SM)
            pygame.draw.rect(surface, PALETTE.line, r, 1, border_radius=RADIUS_SM)
            lw = draw_text(surface, label, "label", PALETTE.text_faint, midleft=(r.x + 10, r.centery)).width
            draw_text(surface, value, "small", color, midleft=(r.x + 10 + lw + 8, r.centery))


@dataclass
class Section:
    """A titled group of blocks; the guide's sidebar lists sections."""

    title: str
    blocks: list[Block]


class Document:
    """Sections laid out one after another. ``anchors`` holds the y of each section's heading."""

    def __init__(self, sections: list[Section], width: int) -> None:
        self.sections = sections
        self.placed: list[tuple[int, Block]] = []      # (y, block)
        self.anchors: list[int] = []
        y = 0
        for section in sections:
            if y:
                y += BLOCK_GAP * 2                     # extra space before each new section
            self.anchors.append(y)
            for block in [Heading(section.title), *section.blocks]:
                self.placed.append((y, block))
                y += block.layout(width) + BLOCK_GAP
        self.height = y

    def draw(self, surface: pygame.Surface, x: int, top: float, view: pygame.Rect) -> None:
        """Draw with the document's top at ``top`` (screen y), skipping blocks outside ``view``."""
        old_clip = surface.get_clip()
        surface.set_clip(view)
        for y, block in self.placed:
            screen_y = round(top + y)
            if screen_y > view.bottom or screen_y + block.height < view.top:
                continue
            block.draw(surface, x, screen_y)
        surface.set_clip(old_clip)
