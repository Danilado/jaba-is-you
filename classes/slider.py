from typing import Union, TYPE_CHECKING, Callable, Any, Optional, List, Sequence, Tuple

import pygame

if TYPE_CHECKING:
    from global_types import SURFACE


class Slider:
    """
    Slider class
    """

    def __init__(self, xpx: float, ypx: float, width: float, height: float, color_rect,
                 circle_center: Tuple[float, float],
                 radius: float, color_circle, action: Optional[Callable[[], Any]]):
        """
        Slider initialisation

        :ivar x: Position abscissa in pixels
        :ivar y: Position ordinate in pixels
        :ivar width: Width in pixels
        :ivar height: Height in pixels
        :ivar color_rect: Bar colour
        :ivar circle_center: Colour of the centre of the circle
        :ivar radius: Circle radius
        :ivar color_circle: Ciricle colour
        :ivar action: Function called when pressed
        """
        self.xpx = xpx
        self.ypx = ypx
        self.width = width
        self.height = height
        self.color_rect = color_rect
        self.circle_center = circle_center
        self.radius = radius
        self.color_circle = color_circle
        self.action = action
        self.flag_action = False

    def draw(self, screen: "SURFACE"):
        """
        Slider rendering method

        :param screen: Surface to draw on
        """
        pygame.draw.rect(screen, self.color_rect, (self.xpx, self.ypx, self.width, self.height), 0)
        pygame.draw.circle(screen, self.color_circle, self.circle_center, self.radius)

    def update(self, events: List[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and self.is_over(pygame.mouse.get_pos()):
                self.flag_action = True
            if event.type == pygame.MOUSEBUTTONUP and self.flag_action:
                self.flag_action = False
        if self.flag_action and self.action:
            self.action()

    def is_over(self, pos: Sequence[Union[int, float]]) -> bool:
        """
        Coordinates check for being inside the slider area

        :param pos: Abscissa and Ordinate to check pointing

        :return: True if the Abscissa and Ordinate are in the slider area, otherwise False.
        """
        if self.xpx < pos[0] < self.xpx + self.width:
            if self.ypx < pos[1] < self.ypx + self.height:
                return True
        return False
