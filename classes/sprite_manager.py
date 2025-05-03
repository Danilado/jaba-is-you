from pathlib import Path
from typing import Dict, Sequence, Optional, Any

import pygame

from classes.base_download_manager import BaseDownloadManager
from classes.palette import Palette
from classes.sprite_info import SpriteInfo
from global_types import COLOR, SURFACE


class SpriteManager(BaseDownloadManager):
    """The class is necessary to set and cache sprites"""
    path = Path("./sprites/")
    url = "https://www.dropbox.com/s/t8h8esomwy2hjol/sprites10-03-22T19-59.zip?dl=1"
    default_colors = {'algae': (5, 2), 'arrow': (5, 2), 'baba': (0, 3), 'badbad': (2, 4), 'banana': (2, 4),
                      'bat': (3, 1), 'bed': (0, 3), 'bee': (2, 4), 'belt': (1, 1), 'bird': (2, 3), 'blob': (5, 2),
                      'boat': (6, 1), 'boba': (6, 2), 'bog': (5, 1), 'bolt': (2, 4), 'bomb': (0, 1), 'book': (2, 3),
                      'bottle': (1, 4), 'box': (6, 2), 'brick': (6, 3), 'bubble': (1, 4), 'bucket': (2, 2),
                      'bug': (6, 2), 'burger': (2, 3), 'cake': (4, 2), 'car': (2, 2), 'cart': (5, 2), 'cash': (5, 2),
                      'cat': (6, 2), 'chair': (6, 2), 'cheese': (2, 4), 'circle': (5, 3), 'cliff': (6, 1),
                      'clock': (1, 3), 'cloud': (1, 4), 'cog': (0, 1), 'crab': (2, 2), 'crystal': (4, 2), 'cup': (1, 3),
                      'dog': (0, 2), 'donut': (4, 1), 'door': (2, 2), 'dot': (0, 3), 'drink': (4, 4), 'drum': (2, 3),
                      'dust': (6, 2), 'ear': (3, 1), 'egg': (0, 3), 'eye': (3, 1), 'fence': (6, 1), 'fire': (2, 3),
                      'fish': (1, 3), 'flag': (2, 4), 'fofo': (5, 2), 'foliage': (6, 0), 'foot': (3, 1), 'fort': (1, 1),
                      'frog': (2, 4), 'fruit': (2, 2), 'fungi': (6, 1), 'fungus': (6, 1), 'flower': (4, 1),
                      'gate': (2, 2), 'gem': (4, 2),
                      'ghost': (4, 2), 'grass': (5, 0), 'guitar': (6, 2), 'hand': (0, 3), 'hedge': (5, 1),
                      'hihat': (2, 4), 'husk': (6, 1), 'husks': (6, 1), 'ice': (1, 2), 'it': (1, 4), 'jelly': (1, 4),
                      'jiji': (2, 3), 'key': (2, 4), 'knight': (2, 2), 'ladder': (2, 3), 'lamp': (2, 4), 'lava': (2, 3),
                      'leaf': (2, 4), 'lever': (0, 2), 'lift': (0, 1), 'lily': (5, 2), 'line': (0, 3), 'lizard': (2, 2),
                      'lock': (0, 2), 'love': (4, 2), 'me': (3, 1), 'mirror': (1, 4), 'monitor': (0, 1), 'moon': (2, 4),
                      'nose': (3, 1), 'orb': (4, 1), 'pawn': (2, 2), 'piano': (1, 3), 'pillar': (0, 1), 'pipe': (1, 1),
                      'pixel': (0, 3), 'pizza': (2, 3), 'plane': (2, 2), 'planet': (2, 3), 'plank': (6, 0),
                      'potato': (6, 1), 'pumpkin': (2, 3), 'reed': (6, 2), 'ring': (2, 3), 'road': (0, 1),
                      'robot': (0, 1), 'rock': (6, 2), 'rocket': (0, 1), 'rose': (2, 2), 'rubble': (6, 1),
                      'sax': (3, 4), 'seed': (6, 2), 'shell': (4, 2), 'shirt': (2, 1), 'shovel': (3, 1), 'sign': (6, 1),
                      'skull': (2, 1), 'spike': (1, 1), 'sprout': (5, 3), 'square': (0, 0), 'star': (2, 4),
                      'statue': (0, 1), 'stick': (6, 1), 'stump': (6, 1), 'sun': (2, 4), 'sword': (1, 4),
                      'table': (6, 1), 'teeth': (0, 3), 'text/algae': (5, 1), 'text/arrow': (5, 2), 'text/baba': (4, 1),
                      'text/badbad': (1, 4), 'text/banana': (2, 4), 'text/bat': (3, 1), 'text/bed': (0, 3),
                      'text/bee': (2, 4), 'text/belt': (1, 3), 'text/bird': (2, 3), 'text/blob': (5, 2),
                      'text/boat': (6, 2), 'text/boba': (6, 2), 'text/bog': (5, 3), 'text/bolt': (2, 4),
                      'text/bomb': (0, 2), 'text/book': (2, 3), 'text/bottle': (1, 4), 'text/box': (6, 1),
                      'text/brick': (6, 1), 'text/bubble': (1, 4), 'text/bucket': (2, 2), 'text/bug': (6, 2),
                      'text/burger': (2, 3), 'text/cake': (4, 2), 'text/car': (2, 2), 'text/cart': (5, 2),
                      'text/cash': (5, 3), 'text/cat': (6, 2), 'text/chair': (6, 2), 'text/cheese': (2, 4),
                      'text/circle': (5, 3), 'text/cliff': (6, 2), 'text/clock': (1, 3), 'text/cloud': (1, 4),
                      'text/cog': (0, 2), 'text/crab': (2, 2), 'text/crystal': (4, 2), 'text/cup': (1, 3),
                      'text/dog': (0, 2), 'text/donut': (4, 2), 'text/door': (2, 2), 'text/dot': (0, 3),
                      'text/drink': (4, 4), 'text/drum': (2, 3), 'text/dust': (2, 4), 'text/ear': (4, 2),
                      'text/egg': (0, 3), 'text/eye': (4, 2), 'text/fence': (6, 1), 'text/fire': (2, 2),
                      'text/fish': (1, 3), 'text/flag': (2, 4), 'text/fofo': (5, 2), 'text/foliage': (2, 3),
                      'text/foot': (4, 2), 'text/fort': (0, 1), 'text/frog': (5, 3), 'text/fruit': (2, 2),
                      'text/fungi': (6, 2), 'text/fungus': (6, 1), 'text/gate': (2, 2), 'text/gem': (4, 2),
                      'text/ghost': (4, 2), 'text/grass': (5, 3), 'text/guitar': (6, 2), 'text/hand': (0, 3),
                      'text/hedge': (5, 1), 'text/hihat': (2, 4), 'text/house': (6, 2), 'text/husk': (6, 1),
                      'text/husks': (6, 2), 'text/ice': (1, 3), 'text/it': (1, 4), 'text/jelly': (1, 4),
                      'text/jiji': (2, 3), 'text/keke': (2, 2), 'text/key': (2, 4), 'text/knight': (2, 2),
                      'text/ladder': (2, 3), 'text/lamp': (2, 4), 'text/lava': (2, 3), 'text/leaf': (2, 4),
                      'text/lever': (0, 2), 'text/lift': (0, 2), 'text/lily': (5, 2), 'text/line': (0, 3),
                      'text/lizard': (2, 2), 'text/lock': (0, 2), 'text/love': (4, 2), 'text/me': (3, 1),
                      'text/mirror': (1, 4), 'text/monitor': (0, 2), 'text/monster': (4, 1), 'text/moon': (2, 4),
                      'text/nose': (4, 2), 'text/orb': (4, 1), 'text/pawn': (2, 2), 'text/piano': (1, 3),
                      'text/pillar': (0, 1), 'text/pipe': (0, 1), 'text/pixel': (0, 3), 'text/pizza': (2, 3),
                      'text/plane': (2, 2), 'text/planet': (2, 3), 'text/plank': (6, 2), 'text/potato': (6, 2),
                      'text/pumpkin': (2, 3), 'text/reed': (6, 2), 'text/ring': (2, 3), 'text/road': (0, 2),
                      'text/robot': (0, 1), 'text/rock': (6, 1), 'text/rocket': (0, 1), 'text/rose': (2, 2),
                      'text/rubble': (6, 1), 'text/sax': (3, 4), 'text/seed': (6, 2), 'text/shell': (4, 2),
                      'text/shirt': (2, 1), 'text/shovel': (4, 2), 'text/sign': (6, 2), 'text/skull': (2, 1),
                      'text/spike': (0, 1), 'text/sprout': (5, 3), 'text/square': (4, 1), 'text/star': (2, 4),
                      'text/statue': (0, 2), 'text/stick': (6, 2), 'text/stump': (6, 2), 'text/sun': (2, 4),
                      'text/sword': (1, 4), 'text/table': (6, 2), 'text/teeth': (0, 3), 'text/tile': (0, 1),
                      'text/tower': (0, 1), 'text/track': (6, 1), 'text/train': (5, 2), 'text/tree': (5, 2),
                      'text/tree2': (5, 2), 'tree2': (5, 2), 'monster': (4, 1), 'keke': (2, 2), 'house': (6, 2),
                      'text/trees': (5, 2), 'text/trumpet': (2, 4), 'text/turnip': (6, 2), 'text/turtle': (5, 4),
                      'text/ufo': (4, 1), 'text/vase': (0, 1), 'text/vine': (5, 2), 'text/wall': (0, 1),
                      'text/water': (1, 3), 'text/what': (0, 3), 'text/wind': (1, 4), 'text/worm': (0, 3),
                      'tile': (1, 0), 'tower': (0, 1), 'track': (6, 0), 'train': (5, 2), 'tree': (5, 2),
                      'trees': (5, 2), 'trumpet': (3, 4), 'turnip': (6, 2), 'turtle': (5, 4), 'ufo': (4, 2),
                      'vase': (0, 2), 'vine': (5, 2), 'wall': (1, 1), 'water': (1, 3), 'what': (0, 3), 'wind': (1, 4),
                      'worm': (0, 3), 'text/3d': (4, 1), 'text/all': (0, 3), 'text/auto': (4, 1), 'text/best': (2, 4),
                      'text/black': (1, 1), 'text/bonus': (4, 1), 'text/boom': (2, 2), 'text/broken': (4, 1),
                      'text/brown': (6, 1), 'text/cyan': (1, 4), 'text/defeat': (2, 1), 'text/deturn': (1, 4),
                      'text/done': (0, 3), 'text/down': (1, 4), 'text/end': (0, 3), 'text/float': (1, 4),
                      'text/green': (5, 2), 'text/grey': (0, 1), 'text/hold': (2, 2), 'text/hot': (2, 3),
                      'text/is': (0, 3), 'text/left': (1, 4), 'text/lime': (5, 3), 'text/lockeddown': (4, 2),
                      'text/lockedleft': (4, 2), 'text/lockedright': (4, 2), 'text/lockedup': (4, 2),
                      'text/melt': (1, 3), 'text/more': (4, 1), 'text/move': (5, 3), 'text/nudgedown': (5, 3),
                      'text/nudgeleft': (5, 3), 'text/nudgeright': (5, 3), 'text/nudgeup': (5, 3), 'text/open': (2, 4),
                      'text/orange': (2, 3), 'text/party': (2, 3), 'text/pet': (4, 2), 'text/phantom': (0, 1),
                      'text/pink': (4, 1), 'text/power': (2, 4), 'text/pull': (6, 2), 'text/purple': (3, 1),
                      'text/push': (6, 1), 'text/red': (2, 2), 'text/reverse': (5, 3), 'text/revert': (2, 3),
                      'text/right': (1, 4), 'text/rosy': (4, 2), 'text/safe': (0, 3), 'text/select': (2, 4),
                      'text/shift': (1, 3), 'text/shut': (2, 2), 'text/silver': (0, 2), 'text/sink': (1, 3),
                      'text/sleep': (1, 4), 'text/still': (2, 2), 'text/stop': (5, 1), 'text/swap': (3, 1),
                      'text/tele': (1, 4), 'text/turn': (1, 4), 'text/up': (1, 4), 'text/weak': (1, 2),
                      'text/white': (0, 3), 'text/win': (2, 4), 'text/wonder': (0, 3), 'text/word': (0, 3),
                      'text/yellow': (2, 4), 'text/you': (4, 1), 'text/you2': (4, 1), 'text/sad': (3, 3),
                      'text/0_n': (0, 1), 'text/10_n': (0, 1), 'cursor': (4, 1), 'text/9_n': (0, 1),
                      'text/1_n': (0, 1), 'text/2_n': (0, 1), 'text/3_n': (0, 1), 'text/4_n': (0, 1),
                      'text/5_n': (0, 1), 'text/6_n': (0, 1), 'text/7_n': (0, 1), 'text/8_n': (0, 1)
                      }

    def __init__(self):
        super().__init__()
        self._sprites: Dict[SpriteInfo, SURFACE] = {}

    def _get_sprite_info(self, *args, **kwargs) -> SpriteInfo:
        def get_from_kwargs(kwarg_key: str, expected_types: Sequence[type]):
            """Function to get `keyword` from kwargs, combined with type checking"""
            kwarg: Optional[Any] = kwargs.pop(kwarg_key, None)
            if kwarg is not None and not isinstance(kwarg, tuple(expected_types)):
                raise TypeError(f"type of keyword `{kwarg_key}` is not "
                                f"{' or '.join(expected_type.__name__ for expected_type in expected_types)}")
            return kwarg

        default: Optional[bool] = get_from_kwargs("default", (bool,))
        palette: Optional[Palette] = get_from_kwargs("palette", (Palette,))
        color: Optional[COLOR] = get_from_kwargs("color", (tuple, str, pygame.color.Color, pygame.Color))

        sprite_info = SpriteInfo(*args, **kwargs)

        if not isinstance(sprite_info.path, Path):
            sprite_info.path = Path(sprite_info.path)

        sprite_info.path = sprite_info.path.with_suffix(".png")

        if color is not None:
            sprite_info.color = color
            return sprite_info

        if default:
            sprite_name = "/".join(sprite_info.path.parts[1:-1])
            if sprite_name in self.default_colors.keys():
                palette_pixel_position = self.default_colors[sprite_name]
                sprite_info.color = palette.pixels[palette_pixel_position[1]][palette_pixel_position[0]]
        return sprite_info

    def get(self, *args, **kwargs) -> SURFACE:
        """
        Function for getting a sprite from the cache. If there is no required sprite in the cache, it will be loaded.

        :keyword path: The path to the sprite, for example sprites/jaba/b00
        :keyword size:
            Sprite size. If this option is set, the modified sprite will be cached, and
            you won't have to modify it every frame.
        :keyword color: Sprite colour
        :return: Returns the loaded sprite via pygame.image.load
        """
        while self.thread.is_alive() and not self.thread_done:
            # Waiting for the sprites to download and unzip
            pygame.time.wait(100)

        sprite_info = self._get_sprite_info(*args, **kwargs)

        if sprite_info not in self._sprites:  # If it's not in the cache
            sprite = pygame.image.load(sprite_info.path)  # Loading sprite
            sprite = sprite.convert_alpha()  # then converting it with alpha channel
            if sprite_info.size is not None:
                sprite = pygame.transform.scale(sprite, sprite_info.size)  # Changing size
            # Then creating colour mask
            color_mask = pygame.Surface(sprite.get_size())
            color_mask.fill(sprite_info.color)  # And filling it with color
            sprite.blit(color_mask, (0, 0),
                        special_flags=pygame.BLEND_MULT)
            self._sprites[sprite_info] = sprite  # And loading sprite into cache

        return self._sprites[sprite_info]  # Returning from cache
