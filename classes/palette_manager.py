from pathlib import Path
from typing import List

import pygame

from classes.palette import Palette
from global_types import COLOR


class PaletteManager:
    palettes_directory = Path("palettes/")

    def __init__(self):
        self._palettes: List[Palette] = []
        for file in PaletteManager.palettes_directory.glob("*.png"):
            image = pygame.image.load(file)
            colors: List[List[COLOR]] = []
            for y_pixel in range(image.get_height()):
                colors.append([])
                for x_pixel in range(image.get_width()):
                    color = image.get_at((x_pixel, y_pixel))[:3]
                    colors[y_pixel].append(color)
            self._palettes.append(Palette(file.stem, colors))

    @property
    def palettes(self) -> List[Palette]:
        return self._palettes

    def get_palette(self, palette_name: str) -> Palette:
        """
        Get the palette in the preloaded cache.

        :param palette_name: Name of the palette in the folder ``palettes/``
        :return: Colour palette.
        :raises ValueError: If the palette does not exist in the folder
        """
        possible_palettes = [palette for palette in self._palettes if palette.name == palette_name]
        if len(possible_palettes) == 0:
            raise ValueError(f"Invalid `palette_name` parameter: {palette_name}")
        return possible_palettes[0]
