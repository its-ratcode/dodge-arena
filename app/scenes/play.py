"""The play scene: input for a run in progress."""

import pygame

from app import config
from app.scenes.base import Scene


class PlayScene(Scene):
    """Moves, casts and pauses. The run itself lives in ``game.world``."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.pause_key = pygame.key.key_code(config.PAUSE_KEY)

    def handle_event(self, event: pygame.event.Event) -> None:
        world = self.game.world
        if event.type == pygame.KEYDOWN:
            if event.key == self.pause_key:
                self.game.pause()
            elif event.key == world.powerup_slot.key:
                world.use_powerup(pygame.mouse.get_pos())
            else:
                for index, slot in enumerate(world.loadout):
                    if event.key == slot.key:
                        world.cast(index, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == config.MOVE_MOUSE_BUTTON:
            world.command_move(event.pos, new_click=True)

    def on_focus_lost(self) -> None:
        self.game.pause()                   # never keep playing in a window you can't see

    def update(self, dt: float) -> None:
        world = self.game.world
        # Holding the move button keeps updating the destination.
        if pygame.mouse.get_pressed()[config.MOVE_MOUSE_BUTTON - 1]:
            world.command_move(pygame.mouse.get_pos(), new_click=False)
        world.update(dt)
        if world.over:
            self.game.end_run()

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw_world(surface)
