from pathlib import Path
from typing import Union

import pygame

from classes.base_download_manager import BaseDownloadManager


class SoundManager(BaseDownloadManager):
    """The class is necessary to set and cache sounds"""
    path = Path("./sounds/")
    url = "https://www.dropbox.com/s/krmadrogtl8tq9k/Music.zip?dl=1"

    def load_music(self, path: Union[Path, str]):
        pygame.mixer.init()
        if not isinstance(path, Path):
            path = Path(path)
        path = str(path.with_suffix(".ogg").resolve())
        if self.thread.is_alive():
            self.thread.join()
        pygame.mixer.music.load(path)
