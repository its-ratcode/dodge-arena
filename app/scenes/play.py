"""The play scene: input for a run in progress."""

import pygame

from app.scenes.base import Scene

LASER_CUES = ("laser_warn", "laser_charge")       # sounds that only warn; the "laser cue" option mutes them


class PlayScene(Scene):
    """Moves, casts and pauses. The run itself lives in ``game.world``.
    Keys and the move button come from the settings, read on every event."""

    def handle_event(self, event: pygame.event.Event) -> None:
        world, settings = self.game.world, self.game.settings
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.key.key_code(settings.keybinds["pause"]):
                self.game.pause()
            elif event.key == world.powerup_slot.key:
                world.use_powerup(pygame.mouse.get_pos())
            else:
                for index, slot in enumerate(world.loadout):
                    if event.key == slot.key:
                        world.cast(index, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == settings.move_button:
            world.command_move(event.pos, new_click=True)

    def on_focus_lost(self) -> None:
        if self.game.settings.options["pause_on_focus_loss"]:
            self.game.pause()               # never keep playing in a window you can't see

    def update(self, dt: float) -> None:
        world = self.game.world
        # Holding the move button keeps updating the destination.
        if pygame.mouse.get_pressed()[self.game.settings.move_button - 1]:
            world.command_move(pygame.mouse.get_pos(), new_click=False)
        world.update(dt * world.rules.game_speed)          # the Game speed assist slows the whole run
        self.play_sounds()
        if world.over:
            self.game.end_run()

    def play_sounds(self) -> None:
        """Play everything the World reported this frame, then forget it."""
        world, audio = self.game.world, self.game.audio
        cues_on = self.game.settings.options["laser_audio_cue"]
        for name in world.events:
            if name.startswith(LASER_CUES) and not cues_on:
                continue                                   # warning beeps and charge-up are optional
            audio.play(name)
        world.events.clear()

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world(surface)
