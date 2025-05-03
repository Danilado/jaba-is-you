from dataclasses import dataclass
from pathlib import Path
from typing import Union, Tuple, Optional

from global_types import COLOR


@dataclass(unsafe_hash=True)
class SpriteInfo:
    """Necessary for proper storage of sprites in the cache"""
    path: Union[Path, str]
    size: Optional[Tuple[int, int]] = None   #: None for default
    color: COLOR = (255, 255, 255)
