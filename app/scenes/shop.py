"""The shop: spend coins on upgrades, or sell them back for exactly what they cost."""

import pygame

from app import config
from app.progression.upgrades import UPGRADES, Upgrade, effect_text
from app.render.icons import draw_icon
from app.render.shapes import draw_panel
from app.render.text import draw_text, text_size
from app.scenes.base import Scene, dim
from app.theme.palette import PALETTE
from app.theme.styles import PANEL_STYLES
from app.ui.widgets import Button, ButtonGroup
from app.util.mathx import lerp_color

COLUMNS = 4
CARD_W, CARD_H, CARD_GAP = 240, 262, 16
GRID_TOP = 118
MESSAGE_TIME = 2.5      # s a "Bought ..." message stays
CONFIRM_TIME = 3.0      # s to click "Refund all" a second time


class ShopScene(Scene):
    """Upgrade cards in a grid. ``back`` is the scene to return to (main menu or game over)."""

    def __init__(self, game, back: Scene) -> None:
        super().__init__(game)
        self.back = back
        self.message = ""
        self.message_timer = 0.0
        self.confirm_timer = 0.0
        self.flash: dict[str, float] = {}      # upgrade id -> 1..0 glow after buying or selling
        grid_w = COLUMNS * CARD_W + (COLUMNS - 1) * CARD_GAP
        self.left = (config.SCREEN_WIDTH - grid_w) // 2

        self.cards: list[tuple[Upgrade, pygame.Rect, Button, Button]] = []
        buttons: list[Button] = []
        for i, upgrade in enumerate(UPGRADES):
            row, col = divmod(i, COLUMNS)
            card = pygame.Rect(self.left + col * (CARD_W + CARD_GAP), GRID_TOP + row * (CARD_H + CARD_GAP),
                               CARD_W, CARD_H)
            buy = Button(self._buy_label(upgrade), self._buy(upgrade), size=(128, 38), sound="buy")
            buy.rect.bottomleft = (card.x + 16, card.bottom - 16)
            sell = Button(self._sell_label(upgrade), self._sell(upgrade), style="label", size=(80, 38), sound="sell")
            sell.rect.bottomright = (card.right - 16, card.bottom - 16)
            self.cards.append((upgrade, card, buy, sell))
            buttons += [buy, sell]

        bottom = config.SCREEN_HEIGHT - 26
        back_button = Button("Back", self.go_back, hotkey="escape", sound="back", size=(200, 44))
        back_button.rect.bottomleft = (self.left, bottom)
        self.refund_all = Button(lambda: "Click again to confirm" if self.confirm_timer > 0 else "Refund all",
                                 self.refund_everything, size=(260, 44))
        self.refund_all.rect.bottomright = (self.left + grid_w, bottom)
        self.group = ButtonGroup(buttons + [back_button, self.refund_all])

    # --- Actions (each returns a function, so every card's buttons know their upgrade) -------------
    def _buy_label(self, upgrade: Upgrade):
        def label() -> str:
            cost = self.game.profile.cost(upgrade.id)
            return "MAX" if cost is None else str(cost)
        return label

    def _sell_label(self, upgrade: Upgrade):
        def label() -> str:
            refund = self.game.profile.refund(upgrade.id)
            return "SELL" if refund is None else f"SELL +{refund}"
        return label

    def _buy(self, upgrade: Upgrade):
        def buy() -> None:
            if self.game.profile.buy(upgrade.id):
                self.say(f"Bought {upgrade.name} (level {self.game.profile.level(upgrade.id)})")
                self.flash[upgrade.id] = 1.0
        return buy

    def _sell(self, upgrade: Upgrade):
        def sell() -> None:
            refund = self.game.profile.sell(upgrade.id)
            if refund is not None:
                self.say(f"Sold a level of {upgrade.name}: +{refund} coins")
                self.flash[upgrade.id] = 1.0
        return sell

    def refund_everything(self) -> None:
        if self.confirm_timer <= 0:
            self.confirm_timer = CONFIRM_TIME
            return
        self.confirm_timer = 0
        total = self.game.profile.sell_all()
        self.say(f"Refunded {total} coins" if total else "Nothing to refund")
        for upgrade in UPGRADES:
            self.flash[upgrade.id] = 1.0

    def say(self, text: str) -> None:
        self.message, self.message_timer = text, MESSAGE_TIME

    def go_back(self) -> None:
        self.game.scene = self.back

    # --- Scene -------------------------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        self.group.handle_event(event)

    def update(self, dt: float) -> None:
        profile = self.game.profile
        for upgrade, _card, buy, sell in self.cards:
            cost = profile.cost(upgrade.id)
            buy.enabled = profile.can_buy(upgrade.id)
            buy.primary = buy.enabled
            buy.icon = "coin" if cost is not None else None
            sell.enabled = profile.level(upgrade.id) > 0
        self.refund_all.enabled = any(profile.levels.values())
        self.message_timer = max(0.0, self.message_timer - dt)
        self.confirm_timer = max(0.0, self.confirm_timer - dt)
        self.flash = {uid: f - dt * 2 for uid, f in self.flash.items() if f - dt * 2 > 0}
        self.group.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(PALETTE.background)
        surface.blit(self.game.background, (0, 0))
        dim(surface, 120)
        draw_text(surface, "SHOP", "heading", PALETTE.text, shadow=True, topleft=(self.left, 26))
        draw_text(surface, "Upgrades last forever. Selling refunds exactly what you paid.", "small",
                  PALETTE.text_dim, topleft=(self.left, 76))
        self.draw_wallet(surface)
        for upgrade, card, _buy, _sell in self.cards:
            self.draw_card(surface, upgrade, card)
        self.group.draw(surface)
        if self.message_timer > 0:
            color = lerp_color(PALETTE.background, PALETTE.text, min(1.0, self.message_timer / 0.4))
            draw_text(surface, self.message, "small", color, shadow=True,
                      center=(config.SCREEN_WIDTH // 2, self.refund_all.rect.centery))

    def draw_wallet(self, surface: pygame.Surface) -> None:
        coins = str(self.game.profile.coins)
        chip = pygame.Rect(0, 0, max(120, text_size(coins, "timer")[0] + 64), 48)
        chip.topright = (config.SCREEN_WIDTH - self.left, 30)
        draw_panel(surface, chip, "chip")
        draw_icon(surface, "coin", (chip.x + 24, chip.centery), 24, PALETTE.coin)
        draw_text(surface, coins, "timer", PALETTE.coin, shadow=True, midleft=(chip.x + 44, chip.centery))

    def draw_card(self, surface: pygame.Surface, upgrade: Upgrade, card: pygame.Rect) -> None:
        profile = self.game.profile
        level = profile.level(upgrade.id)
        color = getattr(PALETTE, upgrade.color_name)
        draw_panel(surface, card, "frame")
        flash = self.flash.get(upgrade.id, 0.0)
        border = lerp_color(PALETTE.line, color, 0.5 if level else 0.0)
        pygame.draw.rect(surface, lerp_color(border, PALETTE.text, flash), card, 2 if level or flash else 1,
                         border_radius=PANEL_STYLES["frame"].radius)

        # Icon badge, name and level pips.
        icon_center = (card.x + 40, card.y + 42)
        pygame.draw.circle(surface, PALETTE.panel_bottom, icon_center, 24)
        pygame.draw.circle(surface, color if level else PALETTE.line, icon_center, 24, 2)
        icon_color = color if level else lerp_color(color, PALETTE.text_faint, 0.5)     # dim until owned
        draw_icon(surface, upgrade.icon, icon_center, 28, icon_color)
        draw_text(surface, upgrade.name, "button", PALETTE.text, shadow=True, topleft=(card.x + 76, card.y + 20))
        for i in range(upgrade.max_level):
            pip = pygame.Rect(card.x + 76 + i * 20, card.y + 50, 16, 6)
            pygame.draw.rect(surface, color if i < level else PALETTE.track, pip, border_radius=3)

        draw_text(surface, upgrade.summary, "small", PALETTE.text_dim, topleft=(card.x + 18, card.y + 82))
        draw_text(surface, "NOW", "label", PALETTE.text_faint, topleft=(card.x + 18, card.y + 116))
        draw_text(surface, effect_text(upgrade, level), "small", PALETTE.text if level else PALETTE.text_faint,
                  topleft=(card.x + 18, card.y + 132))
        draw_text(surface, "NEXT", "label", PALETTE.text_faint, topleft=(card.x + 18, card.y + 160))
        if level < upgrade.max_level:
            draw_text(surface, effect_text(upgrade, level + 1), "small", color, topleft=(card.x + 18, card.y + 176))
        else:
            draw_text(surface, "Fully upgraded", "small", PALETTE.text_faint, topleft=(card.x + 18, card.y + 176))
