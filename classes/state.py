from dataclasses import dataclass
from typing import TYPE_CHECKING, Union, Callable

from global_types import SURFACE

if TYPE_CHECKING:
    from typing import Optional, Type
    from classes.game_state import GameState
    from classes.game_strategy import GameStrategy


@dataclass
class State:
    """
    A structure storing additional information for GameState, e.g. which GameStrategy should be changed.
    Necessary just to change a tuple.

    :cvar game_state: Change in :class:`classes.game_context.GameContext`
    :cvar switch_to: Optional :class:`classes.game_strategy.GameStrategy`.
    """
    game_state: "GameState"
    switch_to: "Optional[Union[Type[GameStrategy], Callable[[SURFACE], GameStrategy]]]" = None
