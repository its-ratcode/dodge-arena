# Dodge Game

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
| R | Restart (after game over) |
| Esc | Quit |
