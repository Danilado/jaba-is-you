from typing import List, Tuple, Dict

import pygame

from global_types import SURFACE

# I don't like all this stuff. the key is delay, the value is time.
_sync: Dict[int, int] = {}


class Animation:
    """
    Animation class

    :ivar sprites: A list of pictures that will change every :attr:`~.Animation.sprite_switch_delay`
    :ivar sprite_switch_delay: Delay in milliseconds between frames
    :ivar position: Position in pixels where it will be rendered
    :ivar synchronize:
        Does it need to be synchronised with the rest of the animations so that frames change at the same time in all animations.
    """

    def __init__(self, sprites: List[pygame.surface.Surface], sprite_switch_delay: int,
                 position: Tuple[int, int], synchronize: bool = True):
        """
        Animation initialisation

        :param sprites: A list of pictures that will change every :attr:`~.Animation.sprite_switch_delay`
        :param sprite_switch_delay: Delay in milliseconds between frames
        :param position: Position in pixels where it will be rendered
        :param synchronize:
            Does it need to be synchronised with the rest of the animations so that frames change at the same time in all animations.
        """
        # quswadress: What was I thinking when I wrote that?
        # if len(sprites) == 0:
        #     raise ValueError("Sprites are empty")
        self.position: Tuple[int, int] = position
        self.sprites: List[pygame.surface.Surface] = sprites
        self.sprite_switch_delay: int = sprite_switch_delay
        self._current_sprites_index: int = 0
        self.synchronize = synchronize
        if synchronize:
            if self.sprite_switch_delay not in _sync:
                _sync[self.sprite_switch_delay] = pygame.time.get_ticks()
            self._timer = _sync[self.sprite_switch_delay]
        else:
            self._timer = pygame.time.get_ticks()

    @property  # Danilado: Isn't that too long a name for a property?
    # quswadress: Long name? Sorry, next time I'll call it _, csi, or just i, and you will figure out what
    # ...this i is for. And seriously, abbreviations are sometimes unclear; I stick to the principle: a lot of letters,
    # ...but immediately understandable. Be thankful that I called GameStrategy like that and not
    # ...AbstractGameGraphicalUserInterfaceStrategy
    def current_sprites_index(self) -> int:
        """
        :getter: Returns the current index of the element in the :attr:`~.Animation.sprites` that is drawn

        :setter:
            Sets the current number of the item that is drawn on the screen in the :attr:`~.Animation.sprites`,
            if number > length of :attr:`~.Animation.sprites` or number is negative, an exception is raised
        """
        return self._current_sprites_index

    @current_sprites_index.setter
    def current_sprites_index(self, value: int):
        if value > len(self.sprites) or value < 0:
            raise ValueError("current sprites index should be lower than length of sprites. "
                             "You might want to use `% len(object.sprites)`")
        self._current_sprites_index = value

    @property
    def current_sprite(self) -> pygame.surface.Surface:
        """
        :getter: Returns the current sprite that is drawn on the screen

        :setter:
            Sets the current sprite that is being rendered on the screen into :attr:`~.Animation.sprites`,
            if the sprite does not exist in :attr:`~.Animation.sprites`, an exception is raised
        """
        return self.sprites[self.current_sprites_index]

    @current_sprite.setter
    def current_sprite(self, value: pygame.Surface):
        try:
            index = self.sprites.index(value)
        except ValueError as error:
            raise ValueError("current sprite should be in sprites") from error
        self.current_sprites_index = index

    def __copy__(self) -> "Animation":
        copy = Animation(
            self.sprites.copy(), self.sprite_switch_delay, self.position, self.synchronize)
        copy._timer = self._timer
        copy.current_sprites_index = self.current_sprites_index
        return copy

    @property
    def is_need_to_switch_frames(self) -> bool:
        return pygame.time.get_ticks() - self._timer >= self.sprite_switch_delay

    def update(self) -> bool:
        """
        :attr:`~.Animation.current_sprite` update.
        """
        if self.is_need_to_switch_frames:
            if self.synchronize:
                _sync[self.sprite_switch_delay] = pygame.time.get_ticks()
                self._timer = _sync[self.sprite_switch_delay]
            else:
                self._timer = pygame.time.get_ticks()
            self.current_sprites_index = (self._current_sprites_index + 1) % len(self.sprites)
            return True
        return False

    def draw(self, screen: SURFACE) -> None:
        """
        Draw the :attr:`~.Animation.current_sprite` to a :attr:`~.Animation.position` in the ``screen``

        :param screen: The screen on which the :attr:`~.Animation.current_sprite` will be rendered.
        """
        screen.blit(self.current_sprite, self.position)
