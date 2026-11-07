# Dodge Arena

A fast-paced top-down arena dodging game built with Python and pygame.

> Work in progress.

## How to play

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

## Coins and upgrades

Coins appear around the arena and vanish after 8 s (they blink first). Big coins are worth 5.
At the end of a run you also get 1 coin for every 5 s you survived.

Coins buy permanent upgrades, and selling one refunds exactly what it cost:

| Upgrade | Per level | Max |
|---|---|---|
| Swift Boots | +5% movement speed | 5 |
| Ability Haste | -6% Shield / Wall / Dash cooldowns | 5 |
| Thick Bubble | +0.3 s Shield | 4 |
| Long Wall | +25 px Wall length | 4 |
| Long Sprint | +0.5 s Sprint | 4 |
| Far Blink | +20 px Blink range | 3 |
| Coin Magnet | +40 px coin pull radius | 4 |

Progress is saved to `save.json` in your user data folder. Delete it to start over:

| OS | Folder |
|---|---|
| Windows | `%APPDATA%\Dodge Arena` |
| macOS | `~/Library/Application Support/Dodge Arena` |
| Linux | `~/.local/share/Dodge Arena` (or `$XDG_DATA_HOME/Dodge Arena`) |

## Getting started

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python -m app
```

## Controls

| Input | Action |
|---|---|
| Right-click | Walk to the clicked point |
| Hold right-click | Keep following the cursor |
| Q / W / E | Shield / Wall / Dash (toward the cursor) |
| D / F | Sprint / Blink (toward the cursor) |
| R | Restart (after game over) |
| Esc | Quit |
