import enum


@enum.unique
class GameState(enum.Enum):
    """Enumeration of changes that GameStrategy can make to GameContext"""
    STOP = enum.auto()  #: Stop the game
    SWITCH = enum.auto()  #: Switch strategy
    BACK = enum.auto()  #: Bring back the past strategy
    FLIP = enum.auto()  #: Draw on the screen
