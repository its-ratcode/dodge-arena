# Dodge Game

A fast-paced top-down arena dodging game built with Python and pygame.

> Work in progress.

## How to play

Bolts fly in from every edge, each one aimed at where you stood when it appeared.
Lasers sweep across the whole arena: a pink lane warns you first, then the beam fires.
Keep moving: one hit ends the run. Survive as long as you can.

Danger rises from 0% to 100% over two minutes: bolts get faster and more frequent,
sometimes come in pairs, and lasers fire more often with shorter warnings.

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
| R | Restart (after game over) |
| Esc | Quit |
