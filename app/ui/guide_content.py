"""The text of the in-game guide.

Every number comes from ``config`` (or the upgrade table) and every key from
the player's settings, so the guide can never disagree with the game.
"""

from app import config
from app.core.settings import MOVE_BUTTONS, Settings
from app.progression.upgrades import UPGRADE_BY_ID, UPGRADES
from app.ui.document import Bullets, Entry, Paragraph, Section
from app.util.keys import key_label


def sec(value: float) -> str:
    return f"{value:g} s"


def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def build_guide(settings: Settings) -> list[Section]:
    key = {action: key_label(name) for action, name in settings.keybinds.items()}
    move = MOVE_BUTTONS[settings.move_button].lower()
    ramp_minutes = config.DANGER_RAMP_TIME / 60

    return [
        Section("Basics", [
            Paragraph(f"Survive as long as you can. Use {move} to walk to a point, or hold it to keep "
                      f"following the cursor. One hit ends the run."),
            Bullets([
                f"Danger rises from 0% to 100% over {ramp_minutes:g} minutes. Threats get faster and more "
                f"frequent, then stay at their worst.",
                f"Abilities and utility spells fire toward the cursor, so aim with the mouse before you press "
                f"the key.",
                f"Press {key['pause']} to pause at any time. The game also pauses when its window loses "
                f"focus (you can turn that off in Settings).",
            ]),
        ]),
        Section("Threats", [
            Entry("bolt", "bolt", "Bolts",
                  "Fly in from every edge, aimed at where you stood when they appeared. They never turn, so "
                  "a short step sideways is usually enough. Later on they sometimes come in pairs.",
                  facts=[("SPEED", f"{config.BOLT_SPEED_START}-{config.BOLT_SPEED_END} px/s"),
                         ("EVERY", f"{config.BOLT_SPAWN_INTERVAL_START:g}-{config.BOLT_SPAWN_INTERVAL_END:g} s"),
                         ("PAIRS", f"up to {pct(config.DOUBLE_SHOT_CHANCE_END)}")]),
            Entry("laser", "laser", "Lasers",
                  "A lane lights up across the whole arena through your position, then a beam fires along "
                  "it. Get out of the lane before the warning ends. Walls don't stop lasers.",
                  facts=[("FIRST AT", sec(config.LASER_FIRST_DELAY)),
                         ("WARNING", f"{config.LASER_WARNING_START:g}-{config.LASER_WARNING_END:g} s"),
                         ("DEADLY FOR", sec(config.LASER_ACTIVE_TIME))]),
        ]),
        Section("Abilities", [
            Paragraph("Short cooldowns: use them often. The box in the ability bar shows the time left."),
            Entry("shield", "shield", "Shield",
                  "A bubble that blocks the next hit, bolt or laser. While it is up, the bubble is your "
                  "hitbox, so it is a little bigger than you.",
                  key=key["shield"], facts=[("COOLDOWN", sec(config.SHIELD_COOLDOWN)),
                                            ("LASTS", sec(config.SHIELD_DURATION))]),
            Entry("wall", "wall", "Wall",
                  "Raises a wall in front of you, across the direction of the cursor. Bolts that touch it "
                  "are destroyed. It blinks just before it disappears.",
                  key=key["wall"], facts=[("COOLDOWN", sec(config.WALL_COOLDOWN)),
                                          ("LASTS", sec(config.WALL_DURATION)),
                                          ("LENGTH", f"{config.WALL_LENGTH} px")]),
            Entry("dash", "dash", "Dash",
                  "A quick dash toward the cursor. You travel the distance, so a bolt in the way can "
                  "still hit you.",
                  key=key["dash"], facts=[("COOLDOWN", sec(config.DASH_COOLDOWN)),
                                          ("RANGE", f"{config.DASH_RANGE} px")]),
        ]),
        Section("Utility spells", [
            Paragraph("Long cooldowns: keep them for emergencies."),
            Entry("sprint", "sprint", "Sprint", "A burst of movement speed.",
                  key=key["sprint"], facts=[("COOLDOWN", sec(config.SPRINT_COOLDOWN)),
                                            ("LASTS", sec(config.SPRINT_DURATION)),
                                            ("SPEED", f"+{pct(config.SPRINT_MULTIPLIER - 1)}")]),
            Entry("blink", "blink", "Blink",
                  "Teleports you instantly toward the cursor: as far as the cursor, up to its range. "
                  "Nothing can hit you on the way, and it cancels a Dash.",
                  key=key["blink"], facts=[("COOLDOWN", sec(config.BLINK_COOLDOWN)),
                                           ("RANGE", f"{config.BLINK_RANGE} px")]),
        ]),
        Section("Power-ups", [
            Paragraph(f"The first power-up appears {sec(config.POWERUP_FIRST_DELAY)} into a run, one at a time. "
                      f"It stays for {sec(config.POWERUP_MAP_LIFETIME)} (the ring shows the time left) and blinks "
                      f"before it goes. Walk over it to hold it, then press {key['powerup']} to use it. A held "
                      f"power-up has one use and expires after {sec(config.POWERUP_HOLD_TIME)}."),
            Entry("stasis", "stasis", "Stasis",
                  "Turns you into a golden statue. Nothing can hit you, but you can't move or cast. A move "
                  "you click during it runs as soon as it ends.",
                  key=key["powerup"], facts=[("LASTS", sec(config.STASIS_DURATION))]),
            Entry("time_warp", "time_warp", "Time Warp",
                  "Bolts, lasers and the timers that spawn them slow down. You keep your full speed. The "
                  "screen turns blue while it lasts.",
                  key=key["powerup"], facts=[("LASTS", sec(config.TIME_WARP_DURATION)),
                                             ("THREAT SPEED", pct(config.TIME_WARP_FACTOR))]),
            Entry("warp", "warp", "Warp", "A long-range Blink toward the cursor.",
                  key=key["powerup"], facts=[("RANGE", f"{config.WARP_RANGE} px")]),
            Entry("nova", "nova", "Nova",
                  "A shockwave that destroys every bolt and laser on screen, even lasers still showing "
                  "their warning.",
                  key=key["powerup"], facts=[("CLEARS", "Everything")]),
            Entry("coin_rush", "coin", "Coin Rush",
                  "For a while coins appear much faster, more of them fit on the field, and each one is "
                  "worth more.",
                  key=key["powerup"], facts=[("LASTS", sec(config.COIN_RUSH_DURATION)),
                                             ("VALUE", f"x{config.COIN_RUSH_MULT}"),
                                             ("EXTRA", f"+{config.COIN_RUSH_EXTRA_COINS} on field")]),
        ]),
        Section("Coins and upgrades", [
            Entry("coin", "coin", "Coins",
                  f"Appear around the arena and vanish after {sec(config.COIN_LIFETIME)}, blinking first. "
                  f"Big coins are worth {config.BIG_COIN_VALUE}. At the end of a run you also get one coin "
                  f"for every {1 / config.COINS_PER_SECOND_SURVIVED:g} s you survived. Leaving a run early "
                  f"still keeps what you picked up.",
                  facts=[("ON FIELD", f"up to {config.COIN_MAX_ON_FIELD}"),
                         ("BIG COIN", f"{pct(config.BIG_COIN_CHANCE)} chance")]),
            Paragraph("Spend coins in the Shop. Upgrades last forever, and selling a level refunds exactly "
                      "what you paid, so trying a different build never costs anything."),
            Bullets([upgrade_line(u) for u in UPGRADES]),
        ]),
        Section("Second Wind", [
            Entry("second_wind", "second_wind", "Second Wind",
                  f"A passive upgrade. When a hit would end your run, Second Wind saves you instead and makes "
                  f"you untouchable for a moment. Then it recharges. The heart right of the ability bar shows "
                  f"when it is ready. The Shield is always used first.",
                  facts=[("UNTOUCHABLE", sec(config.SECOND_WIND_INVULN_TIME)),
                         ("RECHARGE", f"{sec(config.SECOND_WIND_COOLDOWN)} "
                                      f"(-{sec(UPGRADE_BY_ID['second_wind'].step)} per extra level)")]),
        ]),
        Section("Accessibility", [
            Paragraph("Settings > Accessibility changes how the game looks, and Settings > Gameplay how it "
                      "plays. Everything is saved right away."),
            Bullets([
                "Color modes for deuteranopia, protanopia and tritanopia, plus High contrast. You can also "
                "pick your own color for yourself, bolts and lasers.",
                "Threat outlines draw a bright edge around every bolt and laser.",
                "Reduce flashing stops all blinking and pulsing. Reduced motion stops floating, wobbling, "
                "spinning, sliding and smooth scrolling.",
                "Game speed (down to 50%) and longer laser warnings (up to 200%) make runs easier to learn. "
                "Runs with these assists still earn coins, but don't set best times.",
                "Starting danger lets you practise the fast part of a run straight away.",
            ]),
        ]),
        Section("Tips", [
            Bullets([
                "Keep moving in short steps. Bolts are aimed at where you were, not where you are going.",
                "When a laser lane lights up, step out sideways rather than running along it.",
                f"Save Blink ({key['blink']}) for the hit you can't dodge any other way.",
                "A Wall between you and a busy edge buys you a few seconds of calm.",
                "Coin Rush plus Coin Magnet is the fastest way to afford upgrades.",
                "Sell upgrades any time to try a new build: refunds are always full.",
            ]),
        ]),
    ]


def upgrade_line(upgrade) -> str:
    if upgrade.id == "second_wind":
        return f"{upgrade.name}: {upgrade.summary.rstrip('.')} (max level {upgrade.max_level}, see below)."
    per_level = upgrade.effect.format(upgrade.step)
    return f"{upgrade.name}: {per_level} per level (max level {upgrade.max_level})."
