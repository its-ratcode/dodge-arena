"""Engine and gameplay tuning.

Every number that changes how the game runs or plays lives in this module,
so balancing never means hunting through the code.
"""

# --- Window / timing ------------------------------------------------------------
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
FPS = 60
MAX_FRAME_DT = 0.05        # clamp each frame's delta time (s) so a hitch can't teleport things

# --- Arena ------------------------------------------------------------------------
GRID_SPACING = 50          # px between grid lines
GRID_MAJOR_EVERY = 4       # every Nth grid line is drawn brighter
ARENA_BORDER_INSET = 6     # px between the window edge and the arena border

# --- Player -------------------------------------------------------------------------
PLAYER_RADIUS = 16
PLAYER_SPEED = 325         # px/s
MOVE_MOUSE_BUTTON = 3      # pygame button number: 1 = left, 3 = right

# --- Click marker ---------------------------------------------------------------------
CLICK_MARKER_DURATION = 0.4    # s
CLICK_MARKER_RADIUS = 12       # px

# --- Bolts (the threats) ----------------------------------------------------------------
BOLT_SPEED = 400               # px/s
BOLT_SPAWN_INTERVAL = 0.8      # s between bolts
BOLT_LENGTH = 70               # px, along the flight direction
BOLT_WIDTH = 20                # px, across the flight direction
BOLT_SPAWN_MARGIN = 10         # px outside the window edge where bolts appear
FIRST_SPAWN_DELAY = 1.0        # s of calm at the start of a run
