from pathlib import Path
from typing import Dict, Sequence

import pygame

from classes.base_download_manager import BaseDownloadManager
from classes.sprite_info import SpriteInfo
from global_types import SURFACE


class SpriteManager(BaseDownloadManager):
    """Класс необходимый для установки и кеширования спрайтов"""
    path = Path("./sprites/")
    url = "https://www.dropbox.com/s/t8h8esomwy2hjol/sprites10-03-22T19-59.zip?dl=1"

    def __init__(self):
        super().__init__()
        self._sprites: Dict[SpriteInfo, SURFACE] = {}

    def get(self, *args, **kwargs) -> SURFACE:
        """
        Функция для получения спрайта из кэша. Если в кэше нету нужного спрайта, он загрузится и
        сконвертируется используя параметр `alpha`.

        :keyword path: Путь до спрайта, например sprites/jaba/b00
        :keyword alpha: Если этот параметр установлен,будет происходить convert_alpha вместо convert
        :keyword color: Цвет спрайта
        :keyword sprite_info:
            Если вы хотите использовать :class:`~classes.sprite_info.SpriteInfo` вместо передавания аргументов
        :return: Загруженный спрайт через pygame.image.load
        """
        while self.thread.is_alive() and not self.thread_done:
            pygame.time.wait(100)  # Ждём пока скачаются и разархивируются спрайты

        def get_from_kwargs(kwarg_key: str, expected_types: Sequence[type]):
            """Функция получения `keyword` из kwargs, вместе с проверкой типа"""
            kwarg = kwargs.get(kwarg_key, None)
            if kwarg is not None and not isinstance(kwarg, tuple(expected_types)):
                raise TypeError(f"type of keyword `{kwarg_key}` is not "
                                f"{' or '.join(expected_type.__name__ for expected_type in expected_types)}")
            return kwarg

        sprite_info = get_from_kwargs("sprite_info", (SpriteInfo,))
        if sprite_info is None:
            sprite_info = args[0]
        if sprite_info is None or not isinstance(sprite_info, SpriteInfo):
            sprite_info = SpriteInfo(*args, **kwargs)

        if not isinstance(sprite_info.path, Path):
            sprite_info.path = Path(sprite_info.path)

        sprite_info.path = sprite_info.path.with_suffix(".png").resolve()

        if sprite_info not in self._sprites:   # Если нет в кеше
            sprite = pygame.image.load(sprite_info.path)   # Загружаем спрайт
            if sprite_info.have_alpha_channel:   # Если есть альфа канал
                sprite = sprite.convert_alpha()   # Конвертируем с альфа каналом
            else:   # Иначе
                sprite = sprite.convert()   # Просто конвертируем
            color_mask = pygame.Surface(sprite.get_size())   # Затем создаём цветную маску
            color_mask.fill(sprite_info.color)   # И закрашиваем её цветом
            sprite.blit(color_mask, (0, 0),
                        special_flags=pygame.BLEND_MULT)   # Затем цветную маску накладываем на спрайт
            self._sprites[sprite_info] = sprite   # И загружаем спрайт в кэш

        return self._sprites[sprite_info]   # Возвращаем из кэша
