import abc
from typing import List, Optional

import pygame

from classes.state import State
from global_types import SURFACE


class GameStrategy(abc.ABC):
    """
    An abstract class required to define menu rendering in the GameContext.

    :ivar screen: The screen on which all rendering will take place.
    """

    def __init__(self, screen: SURFACE):
        self.screen: SURFACE = screen

    @abc.abstractmethod
    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """

        :param events: Event list
        :param delta_time_in_milliseconds: time elapsed between frames for FPS-independent motion
        :return: the change in game, see :class:`classes.game_state.GameState`

        .. note::
            If this method returns None, nothing, including screen refresh, will happen.
            To refresh the screen, return State(GameState.flip)
        """
        ...

    @abc.abstractmethod
    def on_init(self):
        ...
