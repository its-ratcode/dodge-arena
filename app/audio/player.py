"""The audio player: builds the sounds once and plays them at the volumes from the settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from app import config
from app.audio.sounds import build_sound_bank
from app.audio.synth import Synth

if TYPE_CHECKING:
    from app.core.settings import Settings


class AudioPlayer:
    """If there is no audio device, the game still runs: every call quietly does nothing.

    Loudness = master volume x effects volume x the call's own ``volume``.
    Menu sounds can be switched off on their own, and the same sound never
    retriggers faster than ``SOUND_MIN_GAP`` (so ten coins at once don't
    become one deafening blast).
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.last_played: dict[str, float] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(config.AUDIO_RATE, -16, 1, 512)    # mono 16-bit, small buffer = low delay
            rate, size, channels = pygame.mixer.get_init()
        except (pygame.error, TypeError):                            # no device (get_init returned None)
            return
        if abs(size) != 16:                                          # to_sound writes 16-bit samples
            return
        pygame.mixer.set_num_channels(config.AUDIO_CHANNELS)
        synth = Synth(rate)
        self.sounds = {name: synth.to_sound(samples, channels) for name, samples in build_sound_bank(synth).items()}
        self.enabled = True

    def loudness(self) -> float:
        o = self.settings.options
        return o["master_volume"] / 100 * o["sfx_volume"] / 100

    def play(self, name: str, volume: float = 1.0) -> bool:
        """Play a sound effect. Returns True if it actually started."""
        sound = self.sounds.get(name)
        if not self.enabled or sound is None:
            return False
        now = pygame.time.get_ticks() / 1000
        if now - self.last_played.get(name, -1.0) < config.SOUND_MIN_GAP:
            return False
        loudness = min(1.0, self.loudness() * volume)
        if loudness <= 0:
            return False
        self.last_played[name] = now
        sound.set_volume(loudness)
        sound.play()
        return True

    def ui(self, name: str) -> bool:
        """A menu sound ("hover", "click" ...), unless menu sounds are switched off."""
        if not self.settings.options["ui_sounds"]:
            return False
        return self.play(name if name in self.sounds else f"ui_{name}")
