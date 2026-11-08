"""Player settings: key bindings and options, kept in the ``settings`` section of the save file."""

from app import config
from app.core.storage import SaveFile
from app.util.keys import is_valid_key_name

ACTION_LABELS = {
    "shield": "Shield", "wall": "Wall", "dash": "Dash",
    "sprint": "Sprint", "blink": "Blink",
    "powerup": "Use power-up", "pause": "Pause",
}
MOVE_BUTTONS = {3: "Right click", 1: "Left click"}      # mouse button -> label

# Option name -> default. Each is a simple on/off setting.
DEFAULT_OPTIONS = {
    "pause_on_focus_loss": True,
    "show_fps": False,
}


class Settings:
    """Validated on load, saved after every change.

    ``keybinds`` is one shared dict: the loadout reads keys from it live, so a
    key changed from the pause menu works as soon as you resume.
    """

    SECTION = "settings"

    def __init__(self, save_file: SaveFile) -> None:
        self.save_file = save_file
        self.keybinds = dict(config.DEFAULT_KEYBINDS)
        self.move_button = config.DEFAULT_MOVE_BUTTON
        self.options = dict(DEFAULT_OPTIONS)
        self._load(save_file.section(self.SECTION))

    def _load(self, data: dict) -> None:
        """Take each saved value only if it is valid. Binding through ``bind`` means a
        hand-edited file that uses one key twice still loads with every key unique."""
        binds = data.get("keybinds")
        if isinstance(binds, dict):
            for action in list(self.keybinds):
                if is_valid_key_name(binds.get(action)):
                    self.bind(action, binds[action], save=False)
        if data.get("move_button") in MOVE_BUTTONS:
            self.move_button = data["move_button"]
        options = data.get("options")
        if isinstance(options, dict):
            for name in self.options:
                if isinstance(options.get(name), bool):
                    self.options[name] = options[name]

    def to_dict(self) -> dict:
        return {"keybinds": dict(self.keybinds), "move_button": self.move_button, "options": dict(self.options)}

    def save(self) -> bool:
        return self.save_file.write(self.SECTION, self.to_dict())

    # --- Changes -------------------------------------------------------------------------------
    def bind(self, action: str, key_name: str, save: bool = True) -> None:
        """Bind ``key_name`` to ``action``. If another action had that key, the two swap,
        so no key ever does two things and no action is left unbound."""
        for other, name in self.keybinds.items():
            if name == key_name and other != action:
                self.keybinds[other] = self.keybinds[action]
        self.keybinds[action] = key_name
        if save:
            self.save()

    def cycle_move_button(self) -> None:
        buttons = list(MOVE_BUTTONS)
        self.move_button = buttons[(buttons.index(self.move_button) + 1) % len(buttons)]
        self.save()

    def toggle(self, option: str) -> None:
        self.options[option] = not self.options[option]
        self.save()

    def reset(self) -> None:
        """Everything back to the defaults."""
        self.keybinds.clear()
        self.keybinds.update(config.DEFAULT_KEYBINDS)       # same dict object: the loadout keeps it
        self.move_button = config.DEFAULT_MOVE_BUTTON
        self.options = dict(DEFAULT_OPTIONS)
        self.save()
