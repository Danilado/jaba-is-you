"""Object class module"""
import os
import os.path
from copy import copy
from typing import List, Literal, Optional

import pygame

import settings
from classes.animation import Animation
from classes.palette import Palette
# noinspection PyUnresolvedReferences
from jaba_speedup import SmoothMove
from elements.global_classes import sprite_manager, palette_manager
from global_types import SURFACE
from settings import DEBUG, TEXT_ONLY, SPRITE_ONLY, NOUNS, OPERATORS, PROPERTIES
from utils import get_pressed_direction



# TODO by quswadress
# Too many fields, refactor this please!

# Danilado:
# Not at all. In too many files, objects and their fields are called without defining the variable as Object in loops
# it is probably impossible to do it at all. This means that
# firstly, half of the code will change
# Secondly, you will have to search for all references to objects manually
# Thirdly, the structures themselves look ugly, otherwise you should create classes that are difficult to serialise.
# quswadress:
# #define IamTooLazyToRefactorThis "It's just an excuse for being too lazy to refactor it."
# 1) Half the code will change? So what? IamTooLazyToRefactorThis
# 2) IamTooLazyToRefactorThis
# 3) No argument. But if structures can work with their own data (i.e. have some methods) then no
#    (that's why there is a min-public-methods parameter in pylint). The Palette structure is an example.
# 4) The serialisation part, I don't get it. What's the actual difficulty? If you're talking about the large connection
#   of classes with each other, I don't think it's a serious difficulty, just make a method `serialize_this_shit` that
#   will take in all these classes and return bytes, and that's it.

class Object:
    """
    Rule object, e.g. Jaba, you, is, and, etc.

    :ivar x: Position of the object on the level **grid** along the x-axis
    :ivar y: Position of the object on the level **grid** along the y-axis
    :ivar xpx: Abscissa of the object on the **screen**
    :ivar ypx: Ordinate of the object on the **screen**

    :ivar direction:
        The direction the object is facing at creation time. Can take the following values:
        0 - Up
        1 - Right
        2 - Down
        3 - Left
        Used with rules move, turn, shift et cetera.

    :ivar name: Object name
    :ivar is_text: Field defining whether the object is text or not

    :ivar width: Sprite width
    :ivar height: Sprite height

    :ivar animation: Object animation
    """

    def __init__(self, x: int, y: int, direction: int = 0, name: str = "empty",
                 is_text: bool = True, palette: Optional[Palette] = None,
                 movement_state: int = 0, neighbours=None,
                 turning_side: Literal[0, 1, 2, 3, -1] = -1, animation=None,
                 safe=False, angle_3d: int = 90, is_3d=False, moved=False,
                 num_3d: int = 0, level_size=(32, 18), smooth_movement: Optional[SmoothMove] = None):

        self.status = ''
        self.name: str = name
        if self.name in TEXT_ONLY:
            self.is_text = True
        self.is_text = is_text

        self.turning_side = turning_side
        self.status_of_rotate: Literal[0, 1, 2, 3] = 0
        self.direction = direction
        self.direction_key_map = {
            0: 1,
            1: 0,
            2: 3,
            3: 2,
        }

        if neighbours is None:
            neighbours = []
        self.neighbours: List[List[Object]] = neighbours

        self._x = x
        self._y = y
        self._xpx = x * 50
        self._ypx = y * 50

        self.angle_3d = angle_3d
        self.num_3d = num_3d

        self.width = 50
        self.height = 50

        self.animation: Animation
        self.movement_state = movement_state
        self.animation = animation

        if palette is None:
            palette = palette_manager.get_palette("default")
        self.palette: Palette = palette

        self.is_hide = False
        self.is_hot = False
        self.is_power = False
        self.is_reverse = False
        self.is_safe = safe
        self.locked_sides = []
        self.is_open = False
        self.is_shut = False
        self.is_phantom = False
        self.is_still = False
        self.is_sleep = False
        self.is_weak = False
        self.is_float = False
        self.is_3d = is_3d
        self.level_processor = None
        self.is_fall = False
        self.is_word = False
        self.status_switch_name = 0
        self.has_objects = []

        self.moved = moved
        self.recursively_used = False

        self.level_size = level_size
        if self.name != 'empty' and self.animation is None:
            self.animation = self.animation_init()

        if smooth_movement is None:
            smooth_movement = SmoothMove(self.xpx, self.ypx, 0, 0, 1)
        self._movement: SmoothMove = smooth_movement

    @property
    def movement(self) -> SmoothMove:
        return self._movement

    def reset_movement(self):
        # TODO by quswadress: Add EmptySmoothMove instead of 0, 0, 1
        self._movement = SmoothMove(self.xpx, self.ypx, 0, 0, 1)

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value
        self._xpx = int(value * 50)

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value
        self._ypx = int(value * 50)

    @property
    def xpx(self) -> int:
        return self._xpx

    @xpx.setter
    def xpx(self, value: int):
        self._xpx = value
        self._x = int(value / 50)

    @property
    def ypx(self) -> int:
        return self._ypx

    @ypx.setter
    def ypx(self, value: int):
        self._ypx = value
        self._y = int(value / 50)

    def investigate_neighbours(self):
        """Investigates the neighbours of the object and returns the correct key to the sprite

        :return: The key to choosing the right sprites and animations
        :rtype: int
        """
        key_dict = {
            '': 0,
            'r': 1,
            'u': 2,
            'ur': 3,
            'l': 4,
            'rl': 5,
            'ul': 6,
            'url': 7,
            'b': 8,
            'rb': 9,
            'ub': 10,
            'urb': 11,
            'bl': 12,
            'rbl': 13,
            'ubl': 14,
            'urbl': 15
        }
        char_dict = ['u', 'r', 'b', 'l']
        key = ''
        for index, array in enumerate(self.neighbours):
            for level_object in array:
                if not level_object.is_text and level_object.name == self.name and \
                        char_dict[index] not in key:
                    key += char_dict[index]
        return key_dict[key]

    def animation_init(self) -> Animation:
        """Initialises an object's animation based on its name, "text state", direction, stage of motion, etc."""
        animation = Animation([], 200, (self.xpx, self.ypx))
        if (self.is_text or self.name in TEXT_ONLY) and self.name not in SPRITE_ONLY:
            path = os.path.join('./', 'sprites', 'text')
            animation.sprites = [sprite_manager.get(
                os.path.join(f"{path}", self.name, f"{self.name}_0_{index + 1}"), default=True, palette=self.palette,
                size=(50, 50)) for index in range(0, 3)]
        else:
            path = os.path.join('./', 'sprites', self.name)
            try:
                states = [int(name.split('_')[1]) for name in os.listdir(path) if os.path.isfile(
                    os.path.join(path, name))]
                state_max = max(states)
            except IndexError:
                print(
                    f'{self.name} fucked up while counting states -> probably filename is invalid')
                state_max = 0
            except FileNotFoundError:
                print(
                    f"{self.name} fucked up while searching for files. Probably folder is corrupt \
                    or does not exist. This shouldn't happen in any circumstances")
                state_max = 0

            if settings.DEBUG:
                print(self.__repr__(), end=" ")
                for k in sorted(self.__dict__.keys()):
                    if k.startswith('is_'):
                        print(k, self.__dict__[k], end=', ')
                print()

            try:
                if state_max == 0:
                    animation.sprites = [sprite_manager.get(
                        os.path.join(path, f'{self.name}_0_{index}'), default=True, palette=self.palette, size=(50, 50))
                        for index in range(1, 4)]
                elif state_max == 15:
                    frame = self.investigate_neighbours()
                    animation.sprites = [sprite_manager.get(
                        os.path.join(path, f'{self.name}_{frame}_{index}'), default=True, palette=self.palette,
                        size=(50, 50)) for index in range(1, 4)]
                elif state_max == 3:
                    animation.sprites = [sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_{self.movement_state % 4}_{index}'), default=True,
                        palette=self.palette, size=(50, 50)) for index in range(1, 4)]
                elif state_max == 24:
                    animation.sprites = [sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_{self.direction_key_map[self.direction] * 8}_{index}'), default=True,
                        palette=self.palette, size=(50, 50)) for index in range(1, 4)]
                elif state_max == 27:
                    animation.sprites = [sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_'
                                     f'{self.movement_state % 4 + self.direction_key_map[self.direction] * 8}_'
                                     f'{index}'), default=True, palette=self.palette, size=(50, 50))
                        for index in range(1, 4)]
                elif state_max == 31:
                    keke_state = self.movement_state % 4 + max(self.direction_key_map[self.direction] * 8, 0) - int(
                        self.is_sleep
                    )
                    if keke_state < 0:
                        keke_state = 31
                    animation.sprites = [sprite_manager.get(
                        os.path.join(
                            path,
                            f'{self.name}_'
                            f'{keke_state}_'
                            f'{index}'), default=True, palette=self.palette, size=(50, 50)) for index in range(1, 4)]
                elif DEBUG:
                    print(f'{self.name} somehow fucked up while setting animation')
            except FileNotFoundError:
                if self.movement_state == 0 and DEBUG:
                    print(f'{self.name} somehow fucked up while setting animation')
                else:
                    self.movement_state = 0
                    return self.animation_init()
        return animation

    def _draw_debug(self, screen: SURFACE, matrix: List[List[List["Object"]]]):
        """
        Illuminates the object with colours for quswadress debug.

        .. Cyan::
            The end of the motion, i.e. where the object is moving to.

        .. Magenta:: Start of motion, i.e. where the object is moving from

        .. Orange::
            The position of the object on the matrix. If it is not on the object, then something has gone wrong.
        """
        if not self.movement.done:
            surface = pygame.Surface((50, 50))
            surface.set_alpha(64)
            surface.fill("cyan")
            screen.blit(surface, (self.movement.start_x_pixel + self.movement.x_pixel_delta,
                                  self.movement.start_y_pixel + self.movement.y_pixel_delta),
                        special_flags=pygame.BLEND_RGBA_MULT)
            surface = pygame.Surface((40, 40))
            surface.set_alpha(64)
            surface.fill("magenta")
            screen.blit(surface, (
                self.movement.start_x_pixel + 5,
                self.movement.start_y_pixel + 5
            ), special_flags=pygame.BLEND_RGBA_ADD)
        y = x = None
        for y, line in enumerate(matrix):
            for x, cell in enumerate(line):
                for game_object in cell:
                    if game_object == self:
                        break
                else:
                    continue
                break
            else:
                continue
            break
        if y is not None and x is not None:
            surface = pygame.Surface((45, 45))
            surface.set_alpha(64)
            surface.fill("orange")
            screen.blit(surface, (x * 50 + 2, y * 50 + 2),
                        special_flags=pygame.BLEND_RGBA_ADD)

    def draw(self, screen: SURFACE, matrix: Optional[List[List[List["Object"]]]] = None):
        """Method of object drawing"""
        if matrix is None:
            matrix = []
        new_x_and_y = self._movement.update_x_and_y()
        self.animation.position = self.xpx, self.ypx = new_x_and_y
        if not self.is_hide:
            self.animation.update()
            self.animation.draw(screen)
        if settings.DEBUG:
            self._draw_debug(screen, matrix)

    def unparse(self) -> str:
        """Serialise an object into a string"""
        return f'{self.x} {self.y} {self.direction} {self.name} {self.is_text}'

    def get_index(self, matrix) -> int:
        """Searches the index of the object in the matrix cell to be deleted
        (Workaround by epsinenta)

        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :return: Index of the object in the array cell
        :rtype: int
        """
        for i in range(len(matrix[self.y][self.x])):
            if matrix[self.y][self.x][i].name == self.name and self.text == matrix[self.y][self.x][i].text:
                return i
        return -1

    def move(self, matrix, level_rules, level_processor) -> None:
        """Selecting the motion method (2D or 3D)

        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]_
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param level_processor: The object of the game class in which the object moves.
        :type level_processor: PlayLevel
        """
        if self.is_3d:
            self.move_3d(matrix, level_rules, level_processor)
        else:
            self.move_2d(matrix, level_rules, level_processor)

    def move_2d(self, matrix, level_rules, level_processor) -> None:
        """Method of object movement in 2D

        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param level_processor: The object of the game class in which the object moves.
        :type level_processor: PlayLevel"""
        self.level_processor = level_processor

        if self.turning_side == 0:
            self.moved = self.motion(1, 0, matrix, level_rules)
            self.direction = 1
        elif self.turning_side == 1:
            self.moved = self.motion(0, -1, matrix, level_rules)
            self.direction = 0
        elif self.turning_side == 2:
            self.moved = self.motion(-1, 0, matrix, level_rules)
            self.direction = 3
        elif self.turning_side == 3:
            self.moved = self.motion(0, 1, matrix, level_rules)
            self.direction = 2

    def move_3d(self, matrix, level_rules, level_processor) -> None:
        """Method of object movement in 3D

        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param level_processor: The object of the game class in which the object moves.
        :type level_processor: PlayLevel
        """
        self.level_processor = level_processor
        if self.turning_side == 2:
            matrix[self.y][self.x].pop(self.get_index(matrix))
            self.angle_3d = (self.angle_3d - 90) % 360
            matrix[self.y][self.x].append(copy(self))
        elif self.turning_side == 0:
            matrix[self.y][self.x].pop(self.get_index(matrix))
            self.angle_3d = (self.angle_3d + 90) % 360
            matrix[self.y][self.x].append(copy(self))
        elif self.turning_side == 1:
            if self.angle_3d == 0:
                self.direction = 1
                self.motion(1, 0, matrix, level_rules)
            if self.angle_3d in (180, -180):
                self.direction = 3
                self.motion(-1, 0, matrix, level_rules)
            if self.angle_3d in (90, -270):
                self.direction = 2
                self.motion(0, 1, matrix, level_rules)
            if self.angle_3d in (-90, 270):
                self.direction = 0
                self.motion(0, -1, matrix, level_rules)
        elif self.turning_side == 3:
            pass

    @staticmethod
    def find_side(delta_x, delta_y) -> Optional[str]:
        """Search for direction of movement

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :return: Movement side
        """
        side = None
        if delta_y > 0:
            side = 'down'
        elif delta_y < 0:
            side = 'up'
        if delta_x > 0:
            side = 'right'
        elif delta_x < 0:
            side = 'left'
        return side

    def update_parameters(self, delta_x, delta_y, matrix):
        """Object parameters update

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        """
        self._movement.start_x_pixel = self._xpx
        self._movement.start_y_pixel = self._ypx
        if not self.is_still:
            self.x += delta_x
            self.y += delta_y
        self.animation = None
        self.movement_state += 1
        self.moved = True
        side = self.find_side(delta_x, delta_y)
        if side == 'down':
            self.status_of_rotate = 3
            self.direction = 2
        elif side == 'up':
            self.status_of_rotate = 1
            self.direction = 0
        elif side == 'right':
            self.status_of_rotate = 0
            self.direction = 1
        elif side == 'left':
            self.status_of_rotate = 2
            self.direction = 3
        matrix[self.y][self.x].append(copy(self))
        self._movement.x_pixel_delta = self._xpx - self._movement.start_x_pixel
        self._movement.y_pixel_delta = self._ypx - self._movement.start_y_pixel
        self._movement.rerun(0.05)

    def check_swap(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the swap rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially swap
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        for rule in level_rules:
            if ((not rule_object.is_text and f'{rule_object.name} is swap' in rule.text_rule)
                    or (f'{self.name} is swap' in rule.text_rule and not self.is_phantom) or
                    ('text is swap' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))
                    or ('text is swap' in rule.text_rule and (self.name in TEXT_ONLY or self.is_text))) \
                    and rule.check_fix(self, matrix, level_rules):
                matrix[self.y][self.x].pop(self.get_index(matrix))
                self.update_parameters(delta_x, delta_y, matrix)
                matrix[self.y][self.x].pop(rule_object.get_index(matrix))
                rule_object.update_parameters(-delta_x, -delta_y, matrix)
                return True
        return False

    def check_melt(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the melt rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((f'{self.name} is melt' in rule.text_rule and not self.is_text)
                                or (f'text is melt' in rule.text_rule and (self.name in TEXT_ONLY
                                                                           or self.name in NOUNS and self.is_text)))\
                                and rule.check_fix(self, matrix, level_rules):
                            for sec_rule in level_rules:
                                if not rule_object.is_text and f'{rule_object.name} is hot' in sec_rule.text_rule\
                                        and sec_rule.check_fix(rule_object, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False
                for rule in level_rules:
                    if self.is_hot and ((not rule_object.is_text and f'{rule_object.name} is melt' in rule.text_rule) or
                                        (f'text is melt' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                                or rule_object.is_text)))\
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_weak(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the weak rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.is_safe:
                for rule in level_rules:
                    if ((f'{rule_object.name} is stop' in rule.text_rule and not rule_object.is_text)
                        or (f'text is stop' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text)))\
                            and self.is_weak \
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                        return False
            for rule in level_rules:
                if ((not rule_object.is_text and f'{rule_object.name} is weak' in rule.text_rule) or
                        (f'text is weak' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))) \
                        and rule.check_fix(rule_object, matrix, level_rules):
                    matrix[self.y + delta_y][self.x +
                                             delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_shut_open(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the shut and open rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.is_safe:
                for rule in level_rules:
                    if not rule_object.is_text and self.is_open and f'{rule_object.name} is shut' in rule.text_rule \
                        or self.is_shut and f'{rule_object.name} is open' in rule.text_rule\
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
                        return False
            for rule in level_rules:
                if not rule_object.is_text and self.is_open and f'{rule_object.name} is shut' in rule.text_rule \
                    or self.is_shut and f'{rule_object.name} is open' in rule.text_rule\
                        and rule.check_fix(rule_object, matrix, level_rules):
                    if not self.is_safe:
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                    matrix[self.y + delta_y][self.x +
                                             delta_x].pop(rule_object.get_index(matrix))
                    if not self.is_safe:
                        return False

            return True

    def die(self, delta_j, delta_i, matrix, level_rules):
        self.has_objects = []
        for rule in level_rules:
            if f'{self.name} has' in rule.text_rule:
                self.has_objects.append(rule.text_rule.split()[-1])
        for new_object_name in self.has_objects:
            new_object = Object(
                x=self.x + delta_j,
                y=self.y + delta_i,
                direction=self.direction,
                name=new_object_name,
                is_text=False,
                palette=Palette(self.palette.name, self.palette.pixels.copy())
            )
            new_object.animation = new_object.animation_init()
            matrix[self.y + delta_i][self.x + delta_j].append(new_object)

    def check_defeat(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the defeat rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((not rule_object.is_text and f'{rule_object.name} is defeat' in rule.text_rule) or
                                ('text is defeat' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                         or rule_object.name in NOUNS
                                                                         and rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            for sec_rule in level_rules:
                                if f'{self.name} is you' in sec_rule.text_rule \
                                        and sec_rule.check_fix(self, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False

                                if f'{self.name} is 3d' in sec_rule.text_rule \
                                        and sec_rule.check_fix(self, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False

                for rule in level_rules:
                    if f'{self.name} is defeat' in rule.text_rule \
                            and rule.check_fix(self, matrix, level_rules):
                        for sec_rule in level_rules:
                            if (not rule_object.is_text and f'{rule_object.name} is you' in sec_rule.text_rule) or\
                                    ('text is you' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                          or rule_object.name in NOUNS
                                                                          and rule_object.is_text)) \
                                    and sec_rule.check_fix(rule_object, matrix, level_rules):
                                matrix[self.y + delta_y][self.x +
                                                         delta_x].pop(rule_object.get_index(matrix))
                            elif not rule_object.is_text and f'{rule_object.name} is 3d' in sec_rule.text_rule \
                                    and sec_rule.check_fix(rule_object, matrix, level_rules):
                                matrix[self.y + delta_y][self.x +
                                                         delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_sink(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Checks the sink rule of the object and immediately performs the action if possible

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if the object survived otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((f'{rule_object.name} is sink' in rule.text_rule and not rule_object.is_text) or
                            ('text is sink' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                    or rule_object.name in NOUNS and rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            matrix[self.y][self.x].pop(self.get_index(matrix))
                            matrix[self.y + delta_y][self.x +
                                                     delta_x].pop(rule_object.get_index(matrix))
                            return False
                for rule in level_rules:
                    if ((f'{self.name} is sink' in rule.text_rule and not self.is_text) or
                            ('text is sink' in rule.text_rule and (self.name in TEXT_ONLY
                                                                    or self.name in NOUNS and self.is_text)))\
                            and rule.check_fix(self, matrix, level_rules):
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_win(self, level_rules, rule_object, matrix) -> bool:
        """Checks the win rule of the object and immediately performs the action if possible. In case of victory
        returns the player to the previous menu.

        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True if victory is achieved otherwise False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                for rule in level_rules:
                    if ((f'{rule_object.name} is win' in rule.text_rule and not rule_object.is_text) or
                        ('text is win' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                              or rule_object.name in NOUNS and rule_object.is_text))) \
                            and rule.check_fix(rule_object, matrix, level_rules):
                        for sec_rule in level_rules:

                            if ((f'{self.name} is you' in sec_rule.text_rule and not self.is_text) or
                                    ('text is you' in sec_rule.text_rule and (self.name in TEXT_ONLY
                                                                              or self.name in NOUNS and self.is_text))) \
                                    and rule.check_fix(self, matrix, level_rules) or \
                                ((f'{self.name} is 3d' in sec_rule.text_rule and not self.is_text) or
                                 ('text is 3d' in sec_rule.text_rule and (self.name in TEXT_ONLY
                                                                          or self.name in NOUNS and self.is_text))) \
                                    and rule.check_fix(self, matrix, level_rules):
                                if not self.level_processor.flag_to_win_animation \
                                        and not self.level_processor.flag_to_level_start_animation:
                                    self.level_processor.flag_to_win_animation = True
            return False

    def check_rules(self, delta_x, delta_y, matrix, level_rules, rule_object) -> Literal[True]:
        """Checks all the rules that apply to the object.
        And changes its status based on them.

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: True "That's the way it should be." (c)Vlastelin
        :rtype: bool
        """
        self.status = 'alive'
        if self.can_interact(rule_object, level_rules):
            self.check_win(level_rules, rule_object, matrix)

            if not self.check_melt(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_shut_open(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_defeat(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_sink(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_weak(delta_x, delta_y, matrix, level_rules, rule_object):
                self.status = 'dead'

            elif self.check_swap(delta_x, delta_y, matrix, level_rules, rule_object):
                self.status = 'moved_swap'

        return True

    def object_can_stop(self, rule_object, level_rules, matrix, with_push=False) -> bool:
        """Checks whether collision handling is required with the object

        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :param with_push: Is trying to push the object
        :type with_push: bool
        :return: True if the object handles collisions otherwise False
        :rtype: bool
        """
        status = False
        for rule in level_rules:
            if (f'{rule_object.name} is stop' in rule.text_rule and not rule_object.is_text
                or f'{rule_object.name} is pull' in rule.text_rule and not rule_object.is_text
                or ('text is pull' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))) \
                    and self.can_interact(rule_object, level_rules) and rule.check_fix(rule_object, matrix, level_rules):
                status = True
            if with_push:
                if f'{rule_object.name} is push' in rule.text_rule and not rule_object.is_text \
                        or (rule_object.name in TEXT_ONLY
                            or rule_object.name in NOUNS and rule_object.is_text) \
                        and rule.check_fix(rule_object, matrix, level_rules)\
                        and self.can_interact(rule_object, level_rules, True):
                    status = True
        return status

    def object_can_move(self, level_rules) -> bool:
        """Checks if the object can move depending on the rules
        !!! This interpretation is faster than checking through a list

        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :return: whether the object can move
        :rtype: bool
        """
        status = False
        moveable_rules_list = [
            f'{self.name} is move',
            f'{self.name} is push',
            f'{self.name} is auto',
            f'{self.name} is nudge',
            f'{self.name} is chill',
            f'{self.name} is you',
            f'{self.name} is you2',
            f'{self.name} is fall',
            f'{self.name} is 3d',
        ]
        for rule in level_rules:
            if rule.text_rule in moveable_rules_list or \
                    (self.name in TEXT_ONLY
                     or self.name in NOUNS and self.is_text) and \
                    self.check_valid_range(0, 0):
                status = True
        return status

    def check_valid_range(self, delta_x, delta_y) -> bool:
        """Checks if the matrix is out of bounds
        during movement

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :return: whether it is possible to move in the given direction
        :rtype: bool
        """
        return self.level_size[0] - 1 >= self.x + delta_x >= 0 \
            and self.level_size[1] - 1 >= self.y + delta_y >= 0

    def pull_objects(self, delta_x, delta_y, matrix, level_rules) -> None:
        """Pulls objects with a pull rule

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        """
        if self.check_valid_range(-delta_x, -delta_y):
            for rule_object in matrix[self.y - delta_y][self.x - delta_x]:
                if not rule_object.is_text and rule_object.name in NOUNS:
                    for rule in level_rules:
                        if (f'{rule_object.name} is pull' in rule.text_rule
                            or ('text is pull' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                      or rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            rule_object.motion(
                                delta_x, delta_y, matrix, level_rules, 'pull')

    def check_locked(self, delta_x, delta_y) -> bool:
        """Blocks the sides for movement in case of out of the matrix boundaries by this movement

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :return: Whether an object can move in the direction of its current movement
        :rtype: bool
        """
        side = self.find_side(delta_x, delta_y)
        if side == 'up' and self.y == 0:
            self.locked_sides.append('up')
        elif side == 'left' and self.x == 0:
            self.locked_sides.append('left')
        elif side == 'right' and self.x == self.level_size[0] - 1:
            self.locked_sides.append('right')
        elif side == 'down' and self.y == self.level_size[1] - 1:
            self.locked_sides.append('down')
        if side in self.locked_sides:
            return False
        return True

    def can_interact(self, rule_object, level_rules, status_push=False) -> bool:
        """Is it possible to interact with an object
        (check for float rule)

        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param rule_object: An object with which a moving object could potentially interact
        :type rule_object: Object
        :return: whether the moving object can interact with this object
        :rtype: bool
        """
        status_float_rule_object = False
        status_push_rule_object = False
        self.is_float = False
        for rule in level_rules:
            if (f'{rule_object.name} is float' == rule.text_rule and not rule_object.is_text) or \
                ('text is float' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                        or rule_object.is_text)):
                status_float_rule_object = True
            if status_push:
                if (f'{rule_object.name} is push' in rule.text_rule
                        and not (rule_object.name in TEXT_ONLY
                                 or rule_object.name in NOUNS and rule_object.is_text)) \
                        or (rule_object.name in TEXT_ONLY or rule_object.is_text):
                    status_push_rule_object = True
            if (f'{self.name} is float' == rule.text_rule and not self.is_text) or \
                ('text is float' == rule.text_rule and (self.name in TEXT_ONLY
                                                        or self.is_text)):
                self.is_float = True
        if self.is_float == status_float_rule_object \
                or status_push_rule_object:
            return True
        return False

    def motion(self, delta_x, delta_y, matrix, level_rules, status=None) -> bool:
        """Makes the object move

        :param delta_x: Object shift in the x-axis
        :type delta_x: int
        :param delta_y: Object shift in the y-axis
        :type delta_y: int
        :param matrix: Matrix on which the object is located
        :type matrix: List[List[List[Object]]]
        :param level_rules: Level rules at the moment of movement
        :type level_rules: List[TextRule]
        :param status: object status, defaults to None
        :type status: str, optional
        :return: whether the object will be moved
        :rtype: bool
        """
        if self.check_locked(delta_x, delta_y) and not self.is_sleep and len(matrix[self.y][self.x]) > 0:
            for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                self.check_rules(delta_x, delta_y, matrix,
                                 level_rules, rule_object)
            if self.status == 'dead':
                self.die(delta_x, delta_y, matrix, level_rules)
                return True
            if self.status == 'moved_swap':
                return False
            for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                if rule_object.object_can_stop(rule_object, level_rules, matrix) \
                        and self.can_interact(rule_object, level_rules):
                    return False
            status_motion = 'no collision'
            if self.status == 'alive':
                for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                    if (self.is_phantom or not rule_object.object_can_stop(rule_object, level_rules, matrix, True)
                            or not self.can_interact(rule_object, level_rules, True)) and status_motion is not False:
                        if self.object_can_move(level_rules) and not self.is_still:
                            status_motion = True

                    elif self.is_fall:
                        status_motion = False

                    elif self.object_can_move(level_rules) \
                            and not self.is_still \
                            and status_motion is not False:
                        status_motion = rule_object.motion(
                            delta_x, delta_y, matrix, level_rules, 'push')

                if status_motion is True:
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.pull_objects(delta_x, delta_y,
                                      matrix, level_rules)
                    self.update_parameters(delta_x, delta_y, matrix)
                    return True
                if status_motion is False:
                    return False

            for rule in level_rules:
                if f'{self.name} is push' in rule.text_rule and status == 'push' and not self.is_text \
                        and rule.check_fix(self, matrix, level_rules):
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.update_parameters(delta_x, delta_y, matrix)
                    return True

            for rule in level_rules:
                if ((f'{self.name} is stop' in rule.text_rule and status == 'push')
                    or (f'{self.name} is pull' in rule.text_rule and status == 'push')) \
                        and not self.is_text \
                        and rule.check_fix(self, matrix, level_rules):
                    return False

            if status is None or (self.name in TEXT_ONLY
                                  or self.name in NOUNS and self.is_text):
                matrix[self.y][self.x].pop(self.get_index(matrix))
                self.pull_objects(delta_x, delta_y, matrix, level_rules)
                self.update_parameters(delta_x, delta_y, matrix)

            for rule in level_rules:
                if ((f'{self.name} is pull' in rule.text_rule and status == 'pull' and not self.is_text) or
                    ('text is pull' in rule.text_rule and (self.name in TEXT_ONLY or self.is_text))) \
                        and rule.check_fix(self, matrix, level_rules):
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.pull_objects(delta_x, delta_y, matrix, level_rules)
                    self.update_parameters(delta_x, delta_y, matrix)

            return True
        elif DEBUG:
            print("NOTE: Object can not move. Calling from classes/objects.py->Object.motion()")
        return False

    def check_word(self, level_rules):
        for rule in level_rules:
            if f'{self.name} is word' in rule.text_rule:
                return True
        return False

    def check_events(self, events: List[pygame.event.Event], number):
        """Event handling method

        :param events: Events received during the call
        :type events: List[pygame.event.Event]
        :param number: YOU(/YOU2) object rule number
        :type number: int
        """
        self.turning_side = get_pressed_direction(number == 2)

    def text(self, rule, property):
        return (f'text {property}' in rule.text_rule and (self.name in OPERATORS
                                                          or self.name in PROPERTIES
                                                          or self.name in TEXT_ONLY
                                                          or (self.name in NOUNS and self.is_text)))

    @property
    def is_noun(self) -> bool:
        """Is the object a noun

        :return: Whether the object is a noun
        :rtype: bool
        """
        return (self.name in NOUNS and self.name not in OPERATORS and self.is_text) or self.name in 'text'

    def __copy__(self):
        """Method of object copying

        :return: A copy of the object
        :rtype: Object
        """
        copied_object = Object(
            x=self.x,
            y=self.y,
            direction=self.direction,
            name=self.name,
            is_text=self.is_text,
            palette=Palette(self.palette.name, self.palette.pixels.copy()),
            movement_state=self.movement_state,
            neighbours=None,
            turning_side=self.turning_side,
            animation=self.animation,
            safe=self.is_safe,
            angle_3d=self.angle_3d,
            is_3d=self.is_3d,
            moved=self.moved,
            num_3d=self.num_3d,
            level_size=self.level_size,
            smooth_movement=self._movement
        )
        copied_object.is_sleep = self.is_sleep
        return copied_object

    def __repr__(self):
        result = "text " if self.is_text else ""
        result += self.name
        result += f" {self.x};{self.y}"
        return result
