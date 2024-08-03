from typing import Union, TYPE_CHECKING, Callable, Any, Optional, List, Sequence

import pygame

import settings

if TYPE_CHECKING:
    from elements.global_classes import AbstractButtonSettings
    from global_types import COLOR, SURFACE


class Button:
    """
    Button class

    :ivar x: Position abscissa in pixels
    :ivar y: Position ordinate in pixels
    :ivar width: Width in pixels
    :ivar height: Height in pixels
    :ivar outline: Outline colour
    :ivar button_settings: Colour settings
    :ivar text: Button text
    :ivar action: Function called when pressed
    """

    def __init__(self, x: int, y: int, width: int, height: int, outline: "COLOR",
                 button_settings: "AbstractButtonSettings",
                 text: str = "", action: Optional[Callable[[], Any]] = None):
        """Button initialisation

        :param x: Position abscissa in pixels
        :param y: Position ordinate in pixels
        :param width: Width in pixels
        :param height: Height in pixels
        :param outline: Outline colour
        :param button_settings: Colour settings
        :param text: Button text
        :param action: Function called when pressed
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.scale = settings.WINDOW_SCALE
        self.settings = button_settings
        self.action = action
        self.outline = outline

    def draw(self, screen: "SURFACE"):
        """
        Button rendering method

        :param screen: Surface to draw on
        """
        if self.outline:
            pygame.draw.rect(screen, self.outline, (self.x - 2,
                                                    self.y - 2, self.width + 4, self.height + 4), 0)

        color = self.settings.button_color if not self.is_over(
            pygame.mouse.get_pos()) else self.settings.button_color_hover
        pygame.draw.rect(screen, color, (self.x, self.y,
                                         self.width, self.height), 0)

        if self.text != "":
            pygame.font.init()
            font = pygame.font.Font(
                "fonts/ConsolateElf.ttf", int(self.settings.text_size * self.scale))
            lines = self.text.split('\n')
            text_height = 0
            for index, line in enumerate(lines):
                render_line = font.render(line, True, self.settings.text_color)
                text_height += render_line.get_height()
                screen.blit(
                    render_line,
                    (
                        self.x + (self.width / 2 -
                                  render_line.get_width() / 2),
                        self.y + (self.height / 2 + (text_height / len(lines) *
                                                     (len(lines) // 2 * -1 + index))) -
                        (render_line.get_height() / 2 if len(lines) == 1 else 0)
                    )
                )

    def update(self, events: List[pygame.event.Event]) -> bool:
        """
        Press check method.

        :param events: List of events received by calling pygame.event.get()
        :return: If action was called, True, otherwise False

        .. note::
            If the action is empty, True will still return when clicked.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and self.is_over(pygame.mouse.get_pos()):
                if self.action is not None:
                    self.action()
                return True
        return False

    def is_over(self, pos: Sequence[Union[int, float]]) -> bool:
        """
        Coordinates check for being inside the button area

        :param pos: Abscissa and Ordinate to check pointing

        :return: True if the Abscissa and Ordinate are in the button area, otherwise False.
        """
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False
