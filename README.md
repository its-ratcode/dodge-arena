# Dodge Arena

A fast-paced top-down arena dodging game built with Python and pygame.

> Work in progress.

## How to play

The full guide is in the game: **How to play** on the main menu or the pause menu (key H).
It always shows your current keys and the game's real numbers.

Bolts fly in from every edge, each one aimed at where you stood when it appeared.
Lasers sweep across the whole arena: a pink lane warns you first, then the beam fires.
Keep moving: one hit ends the run. Survive as long as you can.

Danger rises from 0% to 100% over two minutes: bolts get faster and more frequent,
sometimes come in pairs, and lasers fire more often with shorter warnings.

Three abilities help you survive, each aimed with the mouse cursor and on its own cooldown:

| Ability | Effect |
|---|---|
| Shield | A bubble that blocks the next hit (bolt or laser) for 1.5 s |
| Wall | A wall in front of you, across the cursor direction, that destroys bolts for 3 s. Lasers pass through |
| Dash | A fast 200 px dash toward the cursor. You can still be hit on the way |

Two utility spells have long cooldowns, so keep them for emergencies:

| Utility spell | Effect |
|---|---|
| Sprint | +50% movement speed for 3 s |
| Blink | Instantly teleport toward the cursor, up to 160 px. Cancels a dash |

## Power-ups

Every so often a power-up appears on the map (one at a time; it blinks before it vanishes).
Walk over it to pick it up, then press Space to use it. It has one use and expires 25 s after pickup.

| Power-up | Effect |
|---|---|
| Stasis | Frozen in place for 1.5 s: nothing can hit you, but you can't move or cast |
| Time Warp | Bolts, lasers and their spawning slow to 40% for 3 s. You keep your speed |
| Warp | A long Blink, up to 320 px toward the cursor |
| Nova | Destroys every bolt and laser on screen, even lasers still warning |
| Coin Rush | For 8 s coins spawn ~3x as often, more fit on the field, and each is worth double |

## Coins and upgrades

Coins appear around the arena and vanish after 8 s (they blink first). Big coins are worth 5.
At the end of a run you also get 1 coin for every 5 s you survived.

Spend coins in the **Shop** (from the main menu or the game over screen) on permanent upgrades.
Selling a level refunds exactly what it cost, and "Refund all" resets your build:

| Upgrade | Per level | Max |
|---|---|---|
| Swift Boots | +5% movement speed | 5 |
| Ability Haste | -6% Shield / Wall / Dash cooldowns | 5 |
| Thick Bubble | +0.3 s Shield | 4 |
| Long Wall | +25 px Wall length | 4 |
| Long Sprint | +0.5 s Sprint | 4 |
| Far Blink | +20 px Blink range | 3 |
| Coin Magnet | +40 px coin pull radius | 4 |
| Second Wind | Survive one fatal hit, then 1.5 s untouchable. Recharges in 120 s, 30 s less per extra level | 3 |

Progress and settings are saved to `save.json` in your user data folder. Delete it to start over:

| OS | Folder |
|---|---|
| Windows | `%APPDATA%\Dodge Arena` |
| macOS | `~/Library/Application Support/Dodge Arena` |
| Linux | `~/.local/share/Dodge Arena` (or `$XDG_DATA_HOME/Dodge Arena`) |

## Accessibility

Everything is in **Settings** and saved right away:

| Tab | Options |
|---|---|
| Accessibility | Color modes (Deuteranopia, Protanopia, Tritanopia, High contrast), your own color for the player, bolts and lasers, threat outlines, reduce flashing, reduced motion |
| Gameplay | Game speed (50-100%), laser warning time (100-200%), starting danger, pause on focus loss, frame rate |

Runs with a slower game speed or longer laser warnings still earn coins but don't set best times.

## Getting started

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python -m app
```

## Controls

These are the defaults. Every key and the move button can be changed in **Settings**
(click a control, then press the new key; a key already in use swaps places with it).

| Input | Action |
|---|---|
| Right-click | Walk to the clicked point |
| Hold right-click | Keep following the cursor |
| Q / W / E | Shield / Wall / Dash (toward the cursor) |
| D / F | Sprint / Blink (toward the cursor) |
| Space | Use the held power-up |
| Esc | Pause / resume (the game also pauses when its window loses focus) |

Menus work with the mouse or the keyboard: arrows (or Tab) to choose, Enter or Space to confirm,
arrow keys move between cards in the shop, and the key shown on a button triggers it directly
(R = play again / restart, S = shop, M = main menu, Esc = back).
Leaving a run early still banks the coins you picked up.
