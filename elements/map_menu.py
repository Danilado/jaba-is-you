import os
from functools import partial
from typing import List, Optional

import pygame

import settings
from classes.animation import Animation
from classes.cursor import MoveCursor
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.objects import Object
from classes.state import State
from elements.editor import unparse_all
from elements.global_classes import sound_manager, palette_manager, sprite_manager
from elements.loader_util import parse_file
from elements.play_level import PlayLevel
from elements.reference_point import ReferencePoint
from global_types import SURFACE
from settings import STICKY
from utils import map_saves


class MapMenu(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self.matrix: List[List[List[Object]]] = [[[]
                                                  for _ in range(32)] for _ in range(18)]
        self.cursor = MoveCursor()
        self._state: Optional[State] = None
        self.first_iteration = True
        self.current_palette = palette_manager.get_palette('default')
        if settings.FREEMAP:
            self.parse_file('all_map', 'map_levels/open_maps')
        else:
            self.parse_file('map', 'map_levels')
        self.empty_object = Object(-1, -1, 0, 'empty', False)
        self.radius = 0
        self.flag_anime = False
        self.delay = 0
        self.scale = 1
        self.is_6or7_complete = False
        self.count_gate = 0
        self.complete_levels = map_saves()
        self.size = (32, 18)
        self.animation = Animation([], 200, (-30, -30))
        path = os.path.join('./', 'sprites', 'map')
        self.animation.sprites = [sprite_manager.get(
            os.path.join(path, f'map_0_{index}'), default=True,
            size=(1700, 925)) for index in range(1, 4)]

    def set_pallete(self, level_name: str):
        path_to_file = f'./map_levels/{level_name}.omegapog_map_file_type_MLG_1337_228_100500_69_420'
        with open(path_to_file, mode='r', encoding='utf-8') as level_file:
            for line in level_file.readlines():
                parameters = line.strip().split(' ')
                self.current_palette = palette_manager.get_palette(
                    parameters[0])
                break

    def save(self):
        string = f"default {self.size[0]} {self.size[1]}\n"
        string_state, counter = unparse_all(self.matrix)
        if counter > 0:
            string += string_state
            with open("map_levels/map.omegapog_map_file_type_MLG_1337_228_100500_69_420", 'w',
                      encoding='utf-8') as file:
                file.write(string)

    def check_levels(self):
        _, _, all_map_matrix = parse_file('all_map', 'map_levels/open_maps')
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text:
                            if len(all_map_matrix[i][j + 1]) >= 1 and all_map_matrix[i][j + 1][-1].name \
                                    in self.cursor.levels and self.matrix[i][j + 1][-1].name.split("_")[-1] == 'square':
                                self.matrix[i][j + 1].append(Object(j + 1, i, 1,
                                                                    all_map_matrix[i][j +
                                                                                      1][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette(
                                                                        'default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i][j - 1]) >= 1 and all_map_matrix[i][j - 1][-1].name \
                                    in self.cursor.levels and self.matrix[i][j - 1][-1].name.split("_")[-1] == 'square':
                                self.matrix[i][j - 1].append(Object(j - 1, i, 1,
                                                                    all_map_matrix[i][j -
                                                                                      1][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette(
                                                                        'default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i + 1][j]) >= 1 and all_map_matrix[i + 1][j][-1].name \
                                    in self.cursor.levels and self.matrix[i + 1][j][-1].name.split("_")[-1] == 'square':
                                self.matrix[i + 1][j].append(Object(j, i + 1, 1,
                                                                    all_map_matrix[i +
                                                                                   1][j][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette(
                                                                        'default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i - 1][j]) >= 1 and all_map_matrix[i - 1][j][-1].name \
                                    in self.cursor.levels and self.matrix[i - 1][j][-1].name.split("_")[-1] == 'square':
                                self.matrix[i - 1][j].append(Object(j, i - 1, 1,
                                                                    all_map_matrix[i -
                                                                                   1][j][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette(
                                                                        'default'),
                                                                    level_size=(32, 18)))
                            if self.matrix[i][j][-2].name.split('_')[0] in self.cursor.levels:
                                self.matrix[i][j].insert(-2, Object(j, i, 1,
                                                                    f'{self.matrix[i][j][-2].name.split("_")[0]}_n',
                                                                    True,
                                                                    palette=palette_manager.get_palette(
                                                                        'default'),
                                                                    level_size=(32, 18)))
                                self.matrix[i][j].pop(-2)
                            if self.matrix[i][j][-2].name.split('_')[0] == '6' \
                                    or self.matrix[i][j][-2].name.split('_')[0] == '7':
                                _, _, matrix = parse_file(
                                    'part_map_2', 'map_levels/parts_of_map/map')
                                for ix, linex in enumerate(matrix):
                                    for jx, cellx in enumerate(linex):
                                        for _, rule_objectx in enumerate(cellx):
                                            self.matrix[ix][jx].append(
                                                rule_objectx)
                                self.first_iteration = True

        if self.complete_levels['main'] == 1:
            _, _, matrix = parse_file(
                'part_map_1', 'map_levels/parts_of_map/map')
            for i, line in enumerate(matrix):
                for j, cell in enumerate(line):
                    for _, rule_object in enumerate(cell):
                        self.matrix[i][j].append(rule_object)
            self.first_iteration = True

        elif self.complete_levels['reference_point'] == 1:
            _, _, matrix = parse_file(
                'part_map_3', 'map_levels/parts_of_map/map')
            for i, line in enumerate(matrix):
                for j, cell in enumerate(line):
                    for _, rule_object in enumerate(cell):
                        self.matrix[i][j].append(rule_object)
            self.first_iteration = True

        elif self.complete_levels['reference_point'] == 2:
            _, _, matrix = parse_file(
                'part_map_4', 'map_levels/parts_of_map/map')
            for i, line in enumerate(matrix):
                for j, cell in enumerate(line):
                    for _, rule_object in enumerate(cell):
                        self.matrix[i][j].append(rule_object)
            self.first_iteration = True

        elif self.complete_levels['reference_point'] == 3:
            _, _, matrix = parse_file(
                'part_map_5', 'map_levels/parts_of_map/map')
            for i, line in enumerate(matrix):
                for j, cell in enumerate(line):
                    for _, rule_object in enumerate(cell):
                        self.matrix[i][j].append(rule_object)
            self.first_iteration = True

        elif self.complete_levels['reference_point'] == 4:
            for i, line in enumerate(self.matrix):
                for j, cell in enumerate(line):
                    for k, rule_object in enumerate(cell):
                        if rule_object.name == 'gate' and not rule_object.is_text and self.count_gate == 0:
                            self.matrix[i][j].pop()
                            self.matrix[i][j].append(Object(j, i, 1, 'line', False,
                                                            palette=palette_manager.get_palette(
                                                                'default'),
                                                            level_size=(32, 18)))
                            self.count_gate += 1
                            self.first_iteration = True
                            break

        elif self.complete_levels['reference_point'] == 10:
            for i, line in enumerate(self.matrix):
                for j, cell in enumerate(line):
                    for k, rule_object in enumerate(cell):
                        if rule_object.name == 'gate' and not rule_object.is_text:
                            self.matrix[i][j].pop()
                            self.matrix[i][j].append(Object(j, i, 1, 'line', False,
                                                            palette=palette_manager.get_palette(
                                                                'default'),
                                                            level_size=(32, 18)))
                            self.first_iteration = True
                            break
        self.save()

    def animation_level(self):
        if self.flag_anime:
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
                                   offset, self.radius)
            self.radius += 8 * settings.WINDOW_SCALE

    def parse_file(self, level_name: str, path_to_file: str):
        """
        Level Parsing. Adds objects to the :attr:`~.Draw.matrix`.

        :param path_to_file: Folder where the level is stored
        :param level_name: Name of the level in the folder
        :raises OSError: If there's any problem opening the file.
        """
        _, self.size, self.matrix = parse_file(level_name, path_to_file)

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
        offsets = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
        ]
        neighbours = [None for _ in range(4)]
        if x == 0:
            neighbours[0] = [self.empty_object]
        elif x == settings.RESOLUTION[1] // 50 - 1:
            neighbours[2] = [self.empty_object]

        if y == 0:
            neighbours[3] = [self.empty_object]
        elif y == settings.RESOLUTION[0] // 50 - 1:
            neighbours[1] = [self.empty_object]

        for index, offset in enumerate(offsets):
            if neighbours[index] is None:
                neighbours[index] = self.matrix[x + offset[1]][y + offset[0]]
        return neighbours

    def level_name(self):
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text:
                            if self.matrix[i][j][-2].name.split('_')[0] in (*self.cursor.levels,
                                                                            *self.cursor.reference_point):
                                return self.matrix[i][j][-2].name.split('_')[0]

    def go_to_game(self):
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text:
                            if self.matrix[i][j][-2].name.split('_')[0] in self.cursor.levels:
                                if len(self.matrix[i][j][-2].name.split('_')) == 1:
                                    self._state = State(GameState.SWITCH, partial(PlayLevel,
                                                                                  self.matrix[i][j][-2].name[0],
                                                                                  'map_levels', False))
                                else:
                                    self._state = State(GameState.SWITCH, partial(PlayLevel,
                                                                                  self.matrix[i][j][-2].name[0],
                                                                                  'map_levels', True))
                            if self.matrix[i][j][-2].name in self.cursor.reference_point:
                                self._state = State(GameState.SWITCH, partial(ReferencePoint,
                                                                              self.matrix[i][j][-2].name.split("/")[0]))

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Draws the loader interface and handles all events

        :param events: Events collected by the window
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Time between the current frame and the previous frame (unused, sadly)
        :type delta_time_in_milliseconds: int
        :return: Returns the state for proper game_context operation
        """
        map_surface = pygame.Surface((self.size[0] * 50, self.size[1] * 50))
        self._state = None
        saves = map_saves()
        if self.complete_levels['main'] != saves['main']:
            self.complete_levels['main'] = saves['main']
            self.check_levels()
        elif self.complete_levels['reference_point'] != saves['reference_point']:
            self.complete_levels['reference_point'] = saves['reference_point']
            self.check_levels()

        for event in events:
            if event.type == pygame.QUIT:
                self._state = State(GameState.BACK)
                self.save()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = State(GameState.BACK)
                    self.save()
                if event.key == pygame.K_RETURN and self.level_name() in (
                        *self.cursor.levels, *self.cursor.reference_point):
                    self.delay = pygame.time.get_ticks()
                    self.set_pallete(self.level_name())
                    self.flag_anime = True
        if not self.flag_anime:
            self.cursor.check_events()
            needed_to_redraw_objects = self.cursor.turning_side != -1
        else:
            needed_to_redraw_objects = True

        for line in self.matrix:
            for cell in line:
                for game_object in cell:
                    if self.first_iteration:
                        if game_object.name in STICKY and not game_object.is_text:
                            neighbours = self.get_neighbours(
                                game_object.x, game_object.y)
                            game_object.neighbours = neighbours
                            game_object.animation = game_object.animation_init()
                    if game_object.animation.is_need_to_switch_frames:
                        needed_to_redraw_objects = True
        if needed_to_redraw_objects:
            self.screen.fill("black")
            self.animation.update()
            self.animation.draw(map_surface)
            if self._state is None:
                self._state = State(GameState.FLIP)
            self.cursor.move(self.matrix)
            for line in self.matrix:
                for cell in line:
                    for game_object in cell:
                        game_object.draw(map_surface)
            if self.flag_anime and pygame.time.get_ticks() - self.delay > 1500:
                self.flag_anime = False
                self.radius = 0
                self.go_to_game()
            self.screen.blit(pygame.transform.scale(
                map_surface, (self.size[0] * 50 * self.scale * settings.WINDOW_SCALE,
                              self.size[1] * 50 * self.scale * settings.WINDOW_SCALE)), (0, 0))
            self.animation_level()
        if self.first_iteration:
            self.first_iteration = False

        return self._state

    def on_init(self):
        sound_manager.load_music("sounds/Music/burn")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
