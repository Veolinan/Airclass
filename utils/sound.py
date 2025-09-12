# File: utils/sound.py
import os
import pygame

class SoundManager:
    """
    Loads sounds from assets directory. Silent fallback if missing.
    Usage:
      s = SoundManager("assets/sounds")
      s.load("click","click.wav")
      s.play("click")
      s.play_music("theme.mp3")
    """
    def __init__(self, assets_dir="assets/sounds"):
        self.assets_dir = assets_dir
        self.sounds = {}
        # try to init mixer; if fails, flag muted
        self.muted = False
        try:
            pygame.mixer.init()
        except Exception:
            self.muted = True

    def _path(self, filename):
        return os.path.join(self.assets_dir, filename)

    def load(self, name, filename):
        path = self._path(filename)
        if not os.path.isfile(path) or self.muted:
            # keep missing but silent
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except Exception:
            # leave missing quietly
            pass

    def play(self, name):
        s = self.sounds.get(name)
        if s and not self.muted:
            try:
                s.play()
            except Exception:
                pass

    def play_music(self, filename, loop=True):
        path = self._path(filename)
        if not os.path.isfile(path) or self.muted:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
