"""draw_matrix.py hopefully refactored by Gospodin"""
import math
from copy import copy
from random import randint
from typing import List, Optional, Dict, Tuple

import pygame

import settings
from classes import rules
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.objects import Object
from classes.particle import Particle, ParticleStrategy
from classes.ray_casting import raycasting
from classes.state import State
from classes.text_rule import TextRule
from elements.global_classes import sound_manager
from elements.loader_util import parse_file
from global_types import SURFACE
from settings import DEBUG, NOUNS, PROPERTIES, STICKY, VERBS, INFIX, PREFIX, TEXT_ONLY, OPERATORS
from utils import settings_saves, map_saves
from jaba_speedup import copy_matrix  # type: ignore


class PlayLevel(GameStrategy):
    def __init__(self, level_name: str, path_to_level: str, is_complete: bool, screen: SURFACE):
        super().__init__(screen)
        self.old_rules = []
        self.state: Optional[State] = None
        self.show_grid = settings_saves()[0]
        self.path_to_level = path_to_level
        self.is_complete = is_complete

        self.matrix: List[List[List[Object]]] = [
            [[] for _ in range(32)] for _ in range(18)]
        self.start_matrix: List[List[List[Object]]] = [
            [[] for _ in range(32)] for _ in range(18)]
        self.history_of_matrix = []
        self.level_rules = []
        self.delta_cancel = 0

        self.size = (32, 18)
        self.parse_file(level_name, path_to_level)
        self.scale = 1
        self.window_offset: List[int] = [0, 0]
        self.border_screen: pygame.Surface = None
        self.define_border_and_scale()

        self.empty_object = Object(-1, -1, 0, 'empty',
                                   False, self.current_palette)
        self.moved = False

        self.status_cancel = False
        self.first_iteration = True
        self.objects_for_tp = []

        self.win_offsets = [[(775, 325), 0], [(825, 325), 0], [(725, 325), 0], [(875, 325), 0], [(675, 325), 0],
                            [(925, 325), 0], [(625, 325), 0], [(975, 325), 0], [
                                (575, 325), 0], [(1025, 325), 0], [(525, 325), 0], [(1075, 325), 0], [(475, 325), 0],
                            [(1100, 325), 0], [(450, 325), 0], [(1125, 325), 0], [(425, 325), 0]]
        for i, _ in enumerate(self.win_offsets):
            self.win_offsets[i][0] = (
                self.win_offsets[i][0][0] * settings.WINDOW_SCALE, self.win_offsets[i][0][1] * settings.WINDOW_SCALE)

        self.flag_to_win_animation = False
        self.flag_to_delay = False
        self.win_text = self.text_to_png('congratulations')

        self.num_obj_3d = 0
        self.count_3d_obj = 0
        self.flag = True

        self.move_delay = pygame.time.get_ticks()

        self.level_name_object_text = self.text_to_png('level ' + level_name)
        self.flag_to_level_start_animation = True
        self.circle_radius = 650

        self.delay = pygame.time.get_ticks()

        self.particles = [Particle('dot',
                                   ParticleStrategy((randint(0, 1600), randint(-50, 1650)), (950, - 50),
                                                    (randint(20, 35), randint(
                                                        40, 65)), (randint(0, 360), randint(0, 360 * 5)), 20,
                                                    60 + randint(-20, 20), True, True),
                                   self.current_palette.pixels[0][1]) for _ in range(40)]

        self.apply_rules_cache: Dict[str, Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool,
                                                bool, bool, bool, bool, bool, List[str], List[str]]] = {}

    def define_border_and_scale(self):
        if self.size != (32, 18):
            borders: List[pygame.Rect] = [None for _ in range(4)]
            if self.size[1] * 16 / 9 >= self.size[0]:
                if self.size[1] % 2:
                    borders[0] = pygame.Rect(0, 0, 1600, 25)
                    borders[2] = pygame.Rect(0, 875, 1600, 25)
                    self.window_offset[0] = 25
                else:
                    borders[0] = pygame.Rect(0, 0, 1600, 50)
                    borders[2] = pygame.Rect(0, 850, 1600, 50)
                    self.window_offset[0] = 50
                self.scale = (
                    900 - self.window_offset[0] * 2) / (self.size[1] * 50)
                self.window_offset[1] = (
                    1600 - self.size[0] * 50 * self.scale) / 2
                borders[1] = pygame.Rect(0, 0, int(self.window_offset[1]), 900)
                borders[3] = pygame.Rect(
                    int(1600 - self.window_offset[1]), 0, int(self.window_offset[1]), 900)
            else:
                if self.size[0] % 2:
                    borders[1] = pygame.Rect(0, 0, 25, 900)
                    borders[3] = pygame.Rect(1575, 0, 25, 900)
                    self.window_offset[1] = 25
                else:
                    borders[1] = pygame.Rect(0, 0, 50, 900)
                    borders[3] = pygame.Rect(1550, 0, 50, 900)
                    self.window_offset[1] = 50
                self.scale = (
                    1600 - self.window_offset[1] * 2) / (self.size[0] * 50)
                self.window_offset[0] = (
                    900 - self.size[1] * 50 * self.scale) / 2
                borders[0] = pygame.Rect(
                    0, 0, 1600, int(self.window_offset[0]))
                borders[2] = pygame.Rect(
                    0, int(900 - self.window_offset[0]), 1600, int(self.window_offset[0]))
            self.border_screen = pygame.Surface(
                (1600, 900), pygame.SRCALPHA, 32)

            for border in borders:
                pygame.draw.rect(self.border_screen,
                                 self.current_palette.pixels[0][1], border)

            self.border_screen = pygame.transform.scale(
                self.border_screen, (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
            self.border_screen = self.border_screen.convert_alpha()
        else:
            self.border_screen = None
            self.window_offset = [0, 0]

    def parse_file(self, level_name: str, path_to_level: str):
        """
        Level Parsing. Adds objects to :attr:`~.Draw.matrix`.

        .. note::
            If you want to overwrite the map, remember to remove objects from the :attr:`~.Draw.matrix`

        :param level_name: Level name in the levels folder
        :raises OSError: If there's any problem opening the file.
        """
        self.current_palette, self.size, self.start_matrix = parse_file(
            level_name, path_to_level)
        self.matrix = copy_matrix(self.start_matrix)
        if DEBUG:
            print(self.size)

    def get_neighbours(self, y, x) -> List:
        """Looking for cell neighbours on top, right, bottom and left

        :param y: the y-axis coordinate on the matrix comes first
            because the orientation on the matrix is mirrored relative to the normal one
        :type y: int
        :param x: x-axis coordinate on the matrix
        :type x: int
        :return: Array with four neighbouring cells in the order top, right, bottom, left
        :rtype: List[]
        """

        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbours = [[] for _ in range(4)]

        if x == 0:
            neighbours[0] = [self.empty_object]
        elif x == self.size[1] - 1:
            neighbours[2] = [self.empty_object]

        if y == 0:
            neighbours[3] = [self.empty_object]
        elif y == self.size[0] - 1:
            neighbours[1] = [self.empty_object]

        for index, offset in enumerate(offsets):
            if not neighbours[index]:
                neighbours[index] = self.matrix[x + offset[1]][y + offset[0]]

        return neighbours

    @staticmethod
    def remove_copied_rules(arr):
        new_arr = []
        text_arr = []
        for rule in arr:
            if rule.text_rule in text_arr:
                for second_rule in new_arr:
                    if second_rule.text_rule == rule.text_rule:
                        if second_rule.prefix is not None:
                            for pref in rule.prefix:
                                second_rule.prefix.append(pref)
                        for inf in rule.infix:
                            second_rule.infix.append(inf)
            else:
                text_arr.append(rule.text_rule)
                new_arr.append(rule)
        for rule in new_arr:
            if None in rule.infix:
                rule.infix = None
            if rule.prefix is not None and None in rule.prefix:
                rule.prefix = None
        return new_arr

    def form_rule(self, first_object: Object, operator_object: Object, *other_objects: List[Object]):
        rule_string = f'{first_object} {operator_object}'
        for rule_object in other_objects:
            rule_string += f' {rule_object}'
        self.level_rules.append(TextRule(
            rule_string,
            [first_object, operator_object, *other_objects]
        ))
        return len(self.level_rules)

    def check_valid_range(self, x, y, delta_x, delta_y) -> bool:
        """Checks if the matrix is out of bounds during movement

        :param delta_x: Object shift in x-axis
        :type delta_x: int
        :param delta_y: Object shift in y-axis
        :type delta_y: int
        :return: Is it possible to move in this direction
        :rtype: bool
        """
        return self.size[0] - 1 >= x + delta_x >= 0 \
            and self.size[1] - 1 >= y + delta_y >= 0

    def check_not_infix(self, i, j, delta_i, delta_j):
        start_delta_i = delta_i
        start_delta_j = delta_j
        last = None
        while len(self.matrix[i - delta_i][j - delta_j]) != 0:
            for rule_object in self.matrix[i - delta_i][j - delta_j]:
                if last == 'and':
                    if rule_object.is_noun or rule_object.check_word(self.old_rules):
                        last = None
                        delta_j += start_delta_j
                        delta_i += start_delta_i
                elif rule_object.name in INFIX:
                    return True
                elif rule_object.name == 'and':
                    last = 'and'
                    delta_j += start_delta_j
                    delta_i += start_delta_i
                    break
                else:
                    return False
        return False

    def check_noun(self, i, j, delta_i, delta_j, status=None):
        noun_objects = []
        if self.check_valid_range(j, i, 0, 0):
            for first_object in self.matrix[i][j]:
                if first_object.is_noun or first_object.check_word(self.old_rules):
                    cant_be_main = True
                    for second_object in self.matrix[i - delta_i][j - delta_j]:
                        if self.check_not_infix(i, j, delta_i, delta_j) and status == 'main':
                            cant_be_main = False
                    if cant_be_main:
                        noun_objects.append([None, first_object])
                        if self.check_valid_range(j, i, delta_j * 2, delta_i * 2) and status == 'property':
                            for second_objects in self.matrix[i + delta_i][j + delta_j]:
                                if second_objects.name == 'and':
                                    nouns = self.check_noun(i + delta_i * 2, j + delta_j * 2, delta_i, delta_j,
                                                            'property')
                                    if nouns:
                                        for noun in nouns:
                                            noun_objects.append(noun)
                        elif self.check_valid_range(j, i, delta_j * -2, delta_i * -2) and status == 'main':

                            status = None
                            for second_objects in self.matrix[i - delta_i][j - delta_j]:
                                if second_objects.name == 'and':
                                    status = 'and'
                                    nouns = self.check_noun(i + delta_i * -2, j + delta_j * -2, delta_i, delta_j,
                                                            'main')
                                    if nouns:
                                        for noun in nouns:
                                            noun_objects.append(noun)
                            if status is None:
                                if self.check_prefix(i - delta_i, j - delta_j, -delta_i, -delta_j):
                                    prefix = self.check_prefix(
                                        i - delta_i, j - delta_j, -delta_i, -delta_j)
                                    noun_objects = []
                                    for pfix in prefix:
                                        noun_objects.append(
                                            [pfix, first_object])
                                    last_i = prefix[-1].y
                                    last_j = prefix[-1].x
                                    for second_objects in self.matrix[last_i - delta_i][last_j - delta_j]:
                                        if second_objects.name == 'and':
                                            result = self.check_noun(last_i - delta_i * 2,
                                                                     last_j - delta_j * 2,
                                                                     delta_i, delta_j, 'main')
                                            if result:
                                                nouns = result
                                                for noun in nouns:
                                                    noun_objects.append(noun)
                        return noun_objects
        return False

    def check_property(self, i, j, delta_i, delta_j):
        property_objects = []
        if self.check_valid_range(j, i, 0, 0):
            for first_object in self.matrix[i][j]:
                if first_object.name in PROPERTIES:
                    property_objects.append(['', first_object])
                    if self.check_valid_range(j, i, delta_j * 2, delta_i * 2):
                        for second_objects in self.matrix[i + delta_i][j + delta_j]:
                            if second_objects.name == 'and':
                                properties = self.check_property(
                                    i + delta_i * 2, j + delta_j * 2, delta_i, delta_j)
                                if properties:
                                    for object_property in properties:
                                        property_objects.append(
                                            object_property)
                    return property_objects
        return False

    def check_verb(self, i, j, delta_i, delta_j):
        if self.check_valid_range(j, i, 0, 0):
            for first_object in self.matrix[i][j]:
                if first_object.name in VERBS \
                        and self.check_valid_range(j, i, delta_j, delta_i):
                    object_not = None
                    if self.check_valid_range(j, i, delta_j, delta_i):
                        for maybe_not in self.matrix[i + delta_i][j + delta_j]:
                            if maybe_not.name == 'not':
                                delta_i *= 2
                                delta_j *= 2
                                object_not = maybe_not
                    nouns = self.check_noun(
                        i + delta_i, j + delta_j, delta_i, delta_j, 'property')
                    if not nouns:
                        return False
                    if object_not is None:
                        return [[first_object], nouns]
                    return [[first_object], object_not, nouns]

                if first_object.name == 'is' \
                        and self.check_valid_range(j, i, delta_j, delta_i):
                    object_not = None
                    if self.check_valid_range(j, i, delta_j, delta_i):
                        for maybe_not in self.matrix[i + delta_i][j + delta_j]:
                            if maybe_not.name == 'not':
                                delta_i *= 2
                                delta_j *= 2
                                object_not = maybe_not

                    nouns = self.check_noun(
                        i + delta_i, j + delta_j, delta_i, delta_j, 'property')
                    if not nouns:
                        properties = self.check_property(
                            i + delta_i, j + delta_j, delta_i, delta_j)
                        if not properties:
                            return False
                        if object_not is None:
                            return [[first_object], properties]
                        return [[first_object], object_not, properties]
                    if object_not is None:
                        return [[first_object], nouns]
                    return [[first_object], object_not, nouns]
        return False

    def check_infix(self, i, j, delta_i, delta_j):
        if self.check_valid_range(j, i, 0, 0):
            for first_object in self.matrix[i][j]:
                if first_object.name in INFIX \
                        and self.check_valid_range(j, i, delta_j, delta_i):
                    nouns = self.check_noun(
                        i + delta_i, j + delta_j, delta_i, delta_j, 'property')
                    if not nouns:
                        return False
                    return [first_object, nouns]
        return False

    def check_prefix(self, i, j, delta_i, delta_j):
        prefix_objects = []
        if self.check_valid_range(j, i, 0, 0):
            for first_object in self.matrix[i][j]:
                if first_object.name in PREFIX or first_object.name == 'not':
                    prefix_objects.append(first_object)
                    if self.check_valid_range(j, i, delta_j * -2, delta_i * -2):
                        for second_objects in self.matrix[i + delta_i][j + delta_j]:
                            if second_objects.name == 'and':
                                prefix = self.check_prefix(
                                    i + delta_i * 2, j + delta_j * 2, delta_i, delta_j)
                                if isinstance(prefix, list):
                                    for prefix_object in prefix:
                                        prefix_objects.append(prefix_object)
                return prefix_objects
        return False

    def scan_rules(self, i, j, delta_i, delta_j):
        status = True
        verbs = []
        properties = []
        infix = []
        rules = []
        object_not = None
        nouns = self.check_noun(i, j, delta_i, delta_j, 'main')
        if not nouns:
            return False
        if not self.check_infix(i + delta_i, j + delta_j, delta_i, delta_j):
            arguments = self.check_verb(
                i + delta_i, j + delta_j, delta_i, delta_j)
            if not arguments:
                status = False
            else:
                if len(arguments) == 2:
                    verbs = arguments[0]
                    properties = arguments[1]
                if len(arguments) == 3:
                    verbs = arguments[0]
                    object_not = arguments[1]
                    properties = arguments[2]

        else:
            infix = self.check_infix(
                i + delta_i, j + delta_j, delta_i, delta_j)
            arguments = self.check_verb(
                i + delta_i * (len(infix[1]) * 2 + 1), j + delta_j * (len(infix[1]) * 2 + 1), delta_i, delta_j)

            if not arguments:
                status = False
            else:
                if len(arguments) == 2:
                    verbs = arguments[0]
                    properties = arguments[1]
                if len(arguments) == 3:
                    verbs = arguments[0]
                    object_not = arguments[1]
                    properties = arguments[2]

        if status:
            if len(infix) == 0:
                for noun in nouns:
                    for verb in verbs:
                        for object_property in properties:
                            if noun[0] is None:
                                if object_not is None:
                                    text = f'{noun[1].name} {verb.name} {object_property[1].name}'
                                    objects = [noun[1], verb, object_property]
                                    rules.append(
                                        TextRule(text, objects, None, None))
                                else:
                                    text = f'{noun[1].name} {verb.name} {object_not.name} {object_property[1].name}'
                                    objects = [noun[1], verb,
                                               object_not, object_property]
                                    rules.append(
                                        TextRule(text, objects, None, None))
                            else:
                                if object_not is None:
                                    text = f'{noun[1].name} {verb.name} {object_property[1].name}'
                                    objects = [
                                        noun[0], noun[1], verb, object_property]
                                    rules.append(
                                        TextRule(text, objects, noun[0].name, None))
                                else:
                                    text = f'{noun[1].name} {verb.name} ' \
                                           f'{object_not.name} {object_property[1].name}'
                                    objects = [noun[0], noun[1],
                                               verb, object_not, object_property]
                                    rules.append(
                                        TextRule(text, objects, noun[0].name, None))

            elif len(infix) != 0:
                for inf in infix[1]:
                    for noun in nouns:
                        for verb in verbs:
                            for object_property in properties:
                                if noun[0] is None:
                                    if object_not is None:
                                        text = f'{noun[1].name}' \
                                               f' {verb.name} {object_property[1].name}'
                                        objects = [noun[1], infix[0],
                                                   inf[1], verb, object_property[1]]
                                        rules.append(TextRule(text, objects, None, [
                                                     infix[0].name, inf[1].name]))
                                    else:
                                        text = f'{noun[1].name}' \
                                               f' {verb.name} {object_not.name} {object_property[1].name}'
                                        objects = [
                                            noun[1], infix[0], inf[1], verb, object_not, object_property[1]]
                                        rules.append(TextRule(text, objects, None, [
                                                     infix[0].name, inf[1].name]))
                                else:
                                    if object_not is None:
                                        text = f'{noun[1].name} {verb.name} {object_property[1].name}'
                                        objects = [noun[0], noun[1],
                                                   infix[0], inf[1], verb, object_property[1]]
                                        rules.append(
                                            TextRule(text, objects, noun[0].name, [infix[0].name, inf[1].name]))
                                    else:
                                        text = f'{noun[1].name} {verb.name} {object_not.name} {object_property[1].name}'
                                        objects = [noun[0], noun[1], infix[0],
                                                   inf[1], verb, object_not, object_property[1]]
                                        rules.append(
                                            TextRule(text, objects, noun[0].name, [infix[0].name, inf[1].name]))

            for rule in rules:
                self.level_rules.append(rule)

    def on_init(self):
        # TODO by Gospodin: add music choice in editor
        # Issue created.
        sound_manager.load_music("sounds/Music/ruin")

    def text_to_png(self, text):
        if len(text) >= 32:
            x_offset = 0
        else:
            x_offset = (32 - len(text)) // 2
        text_in_objects = []

        for letter in text:
            if letter in TEXT_ONLY:
                img_letter = Object(x_offset, 6, 1, letter,
                                    True, self.current_palette)
                text_in_objects.append(img_letter)
            x_offset += 1

        return text_in_objects

    def level_start_animation(self):
        offsets = [(0 * settings.WINDOW_SCALE, 0 * settings.WINDOW_SCALE), (600 * settings.WINDOW_SCALE, 0),
                   (1000 * settings.WINDOW_SCALE, 0),
                   (1600 * settings.WINDOW_SCALE,
                    0), (0, 900 * settings.WINDOW_SCALE),
                   (300 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE),
                   (800 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE),
                   (1200 * settings.WINDOW_SCALE, 900 *
                    settings.WINDOW_SCALE), (0, 300 * settings.WINDOW_SCALE),
                   (0, 600 * settings.WINDOW_SCALE), (1600 *
                                                      settings.WINDOW_SCALE, 100 * settings.WINDOW_SCALE),
                   (1600 * settings.WINDOW_SCALE, 500 * settings.WINDOW_SCALE),
                   (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE)]
        for offset in offsets:
            pygame.draw.circle(self.screen, self.current_palette.pixels[0][1],
                               offset, self.circle_radius)

        text_surface = pygame.Surface(
            (1600, 900), pygame.SRCALPHA, 32)
        if pygame.time.get_ticks() - self.delay <= 3000:
            for character_object in self.level_name_object_text:
                character_object.draw(text_surface)
        text_surface = pygame.transform.scale(
            text_surface, (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
        text_surface = text_surface.convert_alpha()
        self.screen.blit(text_surface, (0, 0))
        if pygame.time.get_ticks() - self.delay > 3000:
            self.circle_radius -= 8
        if self.circle_radius <= 0:
            self.circle_radius = 0
            self.flag_to_level_start_animation = False

    def win_animation(self):
        border_offsets = [(0 * settings.WINDOW_SCALE, 0 * settings.WINDOW_SCALE), (600 * settings.WINDOW_SCALE, 0),
                          (1000 * settings.WINDOW_SCALE, 0),
                          (1600 * settings.WINDOW_SCALE,
                           0), (0, 900 * settings.WINDOW_SCALE),
                          (300 * settings.WINDOW_SCALE,
                           900 * settings.WINDOW_SCALE),
                          (800 * settings.WINDOW_SCALE,
                           900 * settings.WINDOW_SCALE),
                          (1200 * settings.WINDOW_SCALE,
                           900 * settings.WINDOW_SCALE),
                          (0, 300 * settings.WINDOW_SCALE),
                          (0, 600 * settings.WINDOW_SCALE),
                          (1600 * settings.WINDOW_SCALE,
                           100 * settings.WINDOW_SCALE),
                          (1600 * settings.WINDOW_SCALE,
                           500 * settings.WINDOW_SCALE),
                          (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE)]
        max_radius = 100 * settings.WINDOW_SCALE
        if not self.flag_to_level_start_animation and self.flag_to_win_animation:
            for offset, radius in self.win_offsets:
                pygame.draw.circle(self.screen, self.current_palette.pixels[0][1],
                                   offset, radius)
            if self.win_offsets[0][1] < max_radius:
                self.win_offsets[0][1] += 0.1 * (len(self.win_offsets))
                for index in range(1, len(self.win_offsets), 2):
                    self.win_offsets[index][1] += 0.1 * \
                        (len(self.win_offsets) - index)
                    self.win_offsets[index + 1][1] += 0.1 * \
                        (len(self.win_offsets) - index)

            if self.win_offsets[0][1] >= max_radius and not self.flag_to_delay:
                self.flag_to_delay = True
                self.delay = pygame.time.get_ticks()

            if self.win_offsets[0][1] >= max_radius / 2:
                text_surface = pygame.Surface(
                    (1600, 900), pygame.SRCALPHA, 32)
                for character_object in self.win_text:
                    character_object.draw(text_surface)
                text_surface = pygame.transform.scale(
                    text_surface, (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
                text_surface = text_surface.convert_alpha()
                self.screen.blit(text_surface, (0, 0))

            if self.win_offsets[0][1] >= max_radius and pygame.time.get_ticks() - self.delay >= 1000:
                for offset1 in border_offsets:
                    pygame.draw.circle(
                        self.screen, self.current_palette.pixels[0][1], offset1, self.circle_radius)
                self.circle_radius += 8 * settings.WINDOW_SCALE

            if self.circle_radius >= 650 * settings.WINDOW_SCALE:
                self.upd_map_saves()
                self.state = State(GameState.BACK)

    def upd_map_saves(self):
        if self.path_to_level.split('/')[0] == 'map_levels' and not self.is_complete:
            saves = map_saves()
            if self.path_to_level.split('/')[-1] == 'map_levels':
                saves['main'] += 1
            else:
                saves[self.path_to_level.split('/')[-1]] += 1
            with open('./saves/map_saves', mode='w', encoding='utf-8') as file:
                for param in saves:
                    file.write(f'{param} {saves[param]}\n')

    def functional_event_check(self, events: List[pygame.event.Event]):
        flag = False
        for event in events:
            if event.type == pygame.QUIT:
                self.state = State(GameState.BACK)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = State(GameState.BACK)
                if event.key == pygame.K_z:
                    self.status_cancel = True
                    self.moved = True
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s,
                                 pygame.K_d, pygame.K_SPACE, pygame.K_UP,
                                 pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]:
                    self.moved = True
                    flag = 1
                    self.move_delay = pygame.time.get_ticks()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z:
                    self.status_cancel = False
                    self.moved = True

        if not flag:
            pressed = pygame.key.get_pressed()
            if pygame.time.get_ticks() - 200 > self.move_delay:
                self.move_delay = pygame.time.get_ticks()
                self.moved = any(pressed[key] for key in [pygame.K_w, pygame.K_a, pygame.K_s,
                                                          pygame.K_d, pygame.K_SPACE, pygame.K_UP,
                                                          pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT])

    def detect_iteration_direction(self, events: List[pygame.event.Event], matrix):
        pressed = pygame.key.get_pressed()
        if any(pressed[key] for key in [pygame.K_w, pygame.K_a, pygame.K_SPACE, pygame.K_UP,
                                        pygame.K_LEFT]):
            rules.processor.update_lists(level_processor=self,
                                         matrix=matrix,
                                         events=events)
            for i, line in enumerate(self.matrix):
                for j, cell in enumerate(line):
                    for rule_object in cell:
                        self.apply_rules(matrix, rule_object, i, j)
                        rule_object.reset_movement()
        elif any(pressed[key] for key in [pygame.K_s, pygame.K_d, pygame.K_DOWN, pygame.K_RIGHT]):
            rules.processor.update_lists(level_processor=self,
                                         matrix=matrix,
                                         events=events)
            for i in range(len(self.matrix) - 1, -1, -1):
                for j in range(len(self.matrix[i]) - 1, -1, -1):
                    for rule_object in self.matrix[i][j]:
                        self.apply_rules(matrix, rule_object, i, j)
                        rule_object.reset_movement()

    def _create_in_cache_rules_thing(self, matrix: List[List[List[Object]]], rule_object: Object, i: int, j: int,
                                     rule_cache_key: str):
        is_hot = is_hide = is_safe = is_open = is_shut = is_phantom = \
            is_text = is_still = is_sleep = is_weak = is_float = is_3d = is_fall = is_power = False
        locked_sides: List[str] = []
        has_objects: List[str] = []
        for rule in self.level_rules:
            if rule.check_fix(rule_object, matrix, self.level_rules):
                for noun in NOUNS:
                    if (f'{rule_object.name} is {noun}' == rule.text_rule and not rule_object.is_text) or \
                            (f'text is {noun}' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                      or rule_object.is_text)):
                        if rule_object.status_switch_name == 0:
                            matrix[i][j].pop(rule_object.get_index(matrix))
                            rule_object.name = noun
                            rule_object.is_text = False
                            rule_object.status_switch_name = 1
                            rule_object.animation = rule_object.animation_init()
                            matrix[i][j].append(copy(rule_object))
                        elif rule_object.status_switch_name == 1:
                            rule_object.status_switch_name = 2
                        elif rule_object.status_switch_name == 2:
                            rule_object.status_switch_name = 0
                    if (f'{rule_object.name} has {noun}' == rule.text_rule and not rule_object.is_text) or \
                            (f'text has {noun}' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                       or rule_object.is_text)):
                        has_objects.append(noun)

                if (f'{rule_object.name} is 3d' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is 3d' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                          or rule_object.is_text)):
                    is_3d = True

                elif (f'{rule_object.name} is hide' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is hide' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text)):
                    is_hide = True

                elif (f'{rule_object.name} is fall' == rule.text_rule and not rule_object.is_text) or \
                        (f'text is fall' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                or rule_object.is_text)):
                    is_fall = True

                elif (f'{rule_object.name} is wwak' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is weak' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text)):
                    is_weak = True

                elif (f'{rule_object.name} is hot' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is hot' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                           or rule_object.is_text)):
                    is_hot = True

                elif (f'{rule_object.name} is power' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is power' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                             or rule_object.is_text)):
                    is_power = True

                elif (f'{rule_object.name} is still' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is still' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                             or rule_object.is_text)):
                    is_still = True

                elif (f'{rule_object.name} is locked' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is locked' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                              or rule_object.is_text)):
                    if (f'{rule_object.name} is lockeddown' == rule.text_rule and not rule_object.is_text) or \
                            (f'text is lockeddown' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                          or rule_object.is_text)):
                        locked_sides.append('down')
                    elif (f'{rule_object.name} is lockedup' == rule.text_rule and not rule_object.is_text) or \
                            (f'text is lockedup' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                        or rule_object.is_text)):
                        locked_sides.append('up')
                    elif (f'{rule_object.name} is lockedleft' == rule.text_rule and not rule_object.is_text) or \
                            (f'text is lockedleft' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                          or rule_object.is_text)):
                        locked_sides.append('left')
                    elif (f'{rule_object.name} is lockedright' == rule.text_rule and not rule_object.is_text) or \
                            (f'text is lockedright' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                           or rule_object.is_text)):
                        locked_sides.append('right')

                elif (f'{rule_object.name} is safe' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is safe' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text)):
                    is_safe = True

                elif (f'{rule_object.name} is open' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is open' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text)):
                    is_open = True

                elif (f'{rule_object.name} is phantom' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is phantom' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                               or rule_object.is_text)):
                    is_phantom = True

                elif (f'{rule_object.name} is shut' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is shut' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text)):
                    is_shut = True

                elif f'{rule_object.name} is text' == rule.text_rule and not rule_object.is_text:
                    is_text = True

                elif rule_object.name in TEXT_ONLY or rule_object.is_text:
                    is_text = True

                elif (f'{rule_object.name} is sleep' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is sleep' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                             or rule_object.is_text)):
                    is_sleep = True

                elif (f'{rule_object.name} is float' == rule.text_rule and not rule_object.is_text) or \
                    (f'text is float' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                             or rule_object.is_text)):
                    is_float = True
        self.apply_rules_cache[rule_cache_key] = (is_hot, is_hide, is_safe, is_open, is_shut, is_phantom,
                                                  is_text, is_still, is_sleep, is_power, is_weak,
                                                  is_float, is_3d, is_fall, locked_sides, has_objects)

    def apply_rules(self, matrix: List[List[List[Object]]], rule_object: Object, i: int, j: int):
        rule_cache_key: str = repr(rule_object)
        if rule_cache_key not in self.apply_rules_cache:
            self._create_in_cache_rules_thing(
                matrix, rule_object, i, j, rule_cache_key)
        is_hot, is_hide, is_safe, is_open, is_shut, is_phantom, \
            is_text, is_still, is_sleep, is_power, is_weak, \
            is_float, is_3d, is_fall = self.apply_rules_cache[rule_cache_key][:14]
        locked_sides: List[str] = self.apply_rules_cache[rule_cache_key][14]
        has_objects: List[str] = self.apply_rules_cache[rule_cache_key][15]
        rule_object.is_hot = is_hot
        rule_object.is_power = is_power
        rule_object.is_hide = is_hide
        rule_object.is_safe = is_safe
        rule_object.locked_sides = locked_sides.copy()
        rule_object.is_open = is_open
        rule_object.is_shut = is_shut
        rule_object.is_phantom = is_phantom
        rule_object.is_still = is_still
        rule_object.is_sleep = is_sleep
        rule_object.is_weak = is_weak
        rule_object.is_float = is_float
        rule_object.is_3d = is_3d
        rule_object.is_fall = is_fall
        rule_object.is_text = is_text
        rule_object.has_objects = has_objects
        for rule in self.level_rules:
            if f'{rule_object.name} is you' in rule.text_rule and not rule_object.is_text \
                    or (f'text is you' in rule.text_rule and (rule_object.name in TEXT_ONLY
                        or rule_object.name in NOUNS and rule_object.is_text)):
                rules.processor.update_object(rule_object)
                rules.processor.process(rule)

        for rule in self.level_rules:
            for verb in OPERATORS:
                if (f'{rule_object.name} {verb}' in rule.text_rule and not rule_object.is_text
                    or (f'text {verb}' in rule.text_rule and (rule_object.name in TEXT_ONLY
                        or rule_object.name in NOUNS and rule_object.is_text))) and 'is you' not in rule.text_rule:
                    rules.processor.update_object(rule_object)
                    rules.processor.process(rule)

    def find_rules(self):
        self.level_rules.clear()
        self.old_rules = self.level_rules
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                self.scan_rules(i, j, 0, 1)
                self.scan_rules(i, j, 1, 0)
        self.not_prefix_rules()
        self.mimic_rules()
        self.level_rules = self.remove_copied_rules(
            self.level_rules)

    def not_prefix_rules(self):
        nouns = []
        del_rules = []
        for rule in self.level_rules:
            if rule.prefix is not None:
                if 'not' in rule.prefix:
                    rule_noun = rule.text_rule.split()[0]
                    if len(nouns) == 0:
                        for i in self.matrix:
                            for j in i:
                                for rule_object in j:
                                    if rule_object.name in NOUNS and rule_object.name != rule_noun:
                                        nouns.append(rule_object.name)
                    for noun in nouns:
                        new_rule = copy(rule)
                        text = rule.text_rule.split()
                        text[0] = noun
                        text = f'{text[0]} {text[1]} {text[2]}'
                        new_rule.text_rule = text
                        new_rule.prefix = None
                        if new_rule.infix is not None:
                            for inf in new_rule.infix:
                                if inf is None or None in inf:
                                    new_rule.infix = [None]
                        self.level_rules.append(new_rule)
                    del_rules.append(rule.text_rule)
        new_arr = []
        for rule in self.level_rules:
            if rule.text_rule not in del_rules:
                if rule.prefix is not None:
                    if 'not' not in rule.prefix:
                        new_arr.append(rule)
                else:
                    new_arr.append(rule)

        self.level_rules = new_arr

    def mimic_rules(self):
        new_rules = []
        for mimic_rule in self.level_rules:
            if 'mimic' in mimic_rule.text_rule:
                old_object_name = mimic_rule.text_rule.split()[-1]
                new_object_name = mimic_rule.text_rule.split()[-3]
                for rule in self.level_rules:
                    if f'{old_object_name} is you' in rule.text_rule:
                        new_rule = copy(rule)
                        objects = new_rule.text_rule.split()
                        objects[-3] = new_object_name
                        text = ''
                        for obj in objects:
                            text += obj
                            text += ' '
                        new_rule.text_rule = text[0:-1]
                        new_rules.append(new_rule)

                for rule in self.level_rules:
                    for verb in OPERATORS:
                        if f'{old_object_name} {verb}' in rule.text_rule:
                            new_rule = copy(rule)
                            objects = new_rule.text_rule.split()
                            objects[-3] = new_object_name
                            text = ''
                            for obj in objects:
                                text += obj
                                text += ' '
                            new_rule.text_rule = text[0:-1]
                            new_rules.append(new_rule)
        for rule in new_rules:
            self.level_rules.append(rule)

    def update_sticky_neighbours(self, game_object: Object):
        game_object.neighbours = self.get_neighbours(
            game_object.x, game_object.y)
        game_object.recursively_used = True
        neighbour_list: List[Object]
        for neighbour_list in game_object.neighbours:
            for neighbour in neighbour_list:
                if not neighbour.recursively_used:
                    # neighbour.recursively_used = True
                    self.update_sticky_neighbours(neighbour)
        game_object.animation = game_object.animation_init()
        game_object.moved = False

    def check_matrix(self):
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                for obj in self.matrix[i][j]:
                    if obj.x != j or obj.y != i:
                        obj.animation = obj.animation_init()
                        self.matrix[i][j].pop(obj.get_index(self.matrix))
                        obj.animation = obj.animation_init()
                        self.matrix[i][j].append(copy(obj))
                        obj.animation = obj.animation_init()

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        self.screen.fill(self.current_palette.pixels[4][6])
        self.state = None
        level_3d = False
        count_3d_obj = 0

        self.functional_event_check(events)
        if self.status_cancel:
            new_time = pygame.time.get_ticks()
            if new_time > self.delta_cancel + 200:
                # Slows down with a large number of objects in the matrix. TODO: Need optimization, algorithm is slow
                is_history_of_matrix_not_empty = len(self.history_of_matrix) > 0
                if is_history_of_matrix_not_empty:
                    self.matrix = self.history_of_matrix.pop()
                    self.check_matrix()
                    self.delta_cancel = new_time
                else:
                    self.matrix = copy_matrix(self.start_matrix)
                    self.first_iteration = True
                    self.check_matrix()
                    self.delta_cancel = new_time
                for i in range(len(self.matrix)):
                    for j in range(len(self.matrix[i])):
                        for obj in self.matrix[i][j]:
                            if is_history_of_matrix_not_empty:
                                obj.movement.start_x_pixel = obj.xpx + obj.movement.x_pixel_delta
                                obj.movement.start_y_pixel = obj.ypx + obj.movement.y_pixel_delta
                            else:
                                obj.movement.start_x_pixel = obj.xpx
                                obj.movement.start_y_pixel = obj.ypx
                                obj.movement.x_pixel_delta = obj.movement.y_pixel_delta = 0
                            obj.x = j
                            obj.y = i
                            if is_history_of_matrix_not_empty:
                                obj.movement.x_pixel_delta = obj.xpx - obj.movement.start_x_pixel
                                obj.movement.y_pixel_delta = obj.ypx - obj.movement.start_y_pixel
                            obj.movement.rerun(0.05)

        if self.moved and not self.flag_to_win_animation:
            matrix_copy = copy_matrix(self.matrix)
            self.detect_iteration_direction(events, matrix_copy)
            self.history_of_matrix.append(copy_matrix(self.matrix))
            self.matrix = matrix_copy
            self.find_rules()

            if self.flag:
                for line in self.matrix:
                    for cell in line:
                        for game_object in cell:
                            if game_object.is_3d:
                                game_object.num_3d = self.count_3d_obj
                                self.count_3d_obj += 1
            self.flag = False

        if self.first_iteration:
            self.find_rules()
            self.matrix = copy_matrix(self.start_matrix)

        for line in self.matrix:
            for cell in line:
                for game_object in cell:
                    if game_object.is_3d:
                        level_3d = True
                        if game_object.num_3d == self.num_obj_3d:
                            raycasting(self.screen, (game_object.xpx + int(50 // 2),
                                                     game_object.ypx + int(50 // 2)),
                                       game_object.angle_3d / 180 * math.pi, self.matrix)
                        count_3d_obj += 1

        # TODO by quswadress: And pattern strategy be like: Yeah, yeah, make your big ifs, bloat your classes!
        if level_3d:
            if self.count_3d_obj != count_3d_obj:
                self.count_3d_obj = 0
                for line in self.matrix:
                    for cell in line:
                        for game_object in cell:
                            if game_object.is_3d:
                                game_object.num_3d = self.count_3d_obj
                                self.count_3d_obj += 1

            if count_3d_obj != 0:
                self.num_obj_3d %= self.count_3d_obj
        else:
            rules.processor.on_every_frame()
            level_surface = pygame.Surface(
                (self.size[0] * 50, self.size[1] * 50))
            level_surface.fill(self.current_palette.pixels[4][6])

            for particle in self.particles:
                particle.draw(level_surface)

            for line in self.matrix:
                for cell in line:
                    for game_object in cell:
                        if self.first_iteration or self.moved:
                            if game_object.name in STICKY and not game_object.is_text and (game_object.moved or self.first_iteration):
                                self.update_sticky_neighbours(game_object)
                        game_object.draw(level_surface, self.matrix)

            if self.show_grid:
                for x in range(0, self.size[0] * 50, 50):
                    for y in range(0, self.size[1] * 50, 50):
                        pygame.draw.rect(
                            level_surface, (255, 255, 255), (x, y, 50, 50), 1)

            self.screen.blit(pygame.transform.scale(
                level_surface, (self.size[0] * 50 * self.scale * settings.WINDOW_SCALE,
                                self.size[1] * 50 * self.scale * settings.WINDOW_SCALE)),
                             (self.window_offset[1] * settings.WINDOW_SCALE,
                              self.window_offset[0] * settings.WINDOW_SCALE))

            if self.border_screen:
                self.screen.blit(self.border_screen, (0, 0))

        self.first_iteration = False

        if self.flag_to_level_start_animation:
            self.level_start_animation()

        if self.flag_to_win_animation:
            self.win_animation()

        if self.moved:

            self.moved = False

        if self.state is None:
            self.state = State(GameState.FLIP, None)
        return self.state
