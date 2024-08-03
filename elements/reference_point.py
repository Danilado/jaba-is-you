from functools import partial
from typing import List, Optional

import pygame

import settings
from classes.cursor import MoveCursor
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.objects import Object
from classes.state import State
from elements.editor import unparse_all
from elements.global_classes import sound_manager, palette_manager
from elements.loader_util import parse_file
from elements.play_level import PlayLevel
from global_types import SURFACE
from settings import STICKY
from utils import map_saves


class ReferencePoint(GameStrategy):
    def __init__(self, name: str, screen: SURFACE):
        super().__init__(screen)
        self.levels_passed = 0
        self.matrix: List[List[List[Object]]] = [[[]
                                                  for _ in range(32)] for _ in range(18)]
        self.cursor = MoveCursor()
        self.ref_point_name = name
        self._state: Optional[State] = None
        self.first_iteration = True
        self.level_palette = palette_manager.get_palette('default')
        self.parse_file(name, 'map_levels')
        self.empty_object = Object(-1, -1, 0, 'empty', False)
        self.radius = 0
        self.complete_levels = map_saves()
        self.flag_anime = False
        self.delay = 0
        self.current_palette = palette_manager.get_palette('default')
        self.scale = 1
        self.size = (32, 18)
        self.win_offsets = [[(775, 325), 0], [(825, 325), 0], [(725, 325), 0], [(875, 325), 0], [(675, 325), 0],
                            [(925, 325), 0], [(625, 325), 0], [(975, 325), 0], [
                                (575, 325), 0], [(1025, 325), 0], [(525, 325), 0], [(1075, 325), 0], [(475, 325), 0],
                            [(1100, 325), 0], [(450, 325), 0], [(1125, 325), 0], [(425, 325), 0]]
        for i, _ in enumerate(self.win_offsets):
            self.win_offsets[i][0] = (
                self.win_offsets[i][0][0] * settings.WINDOW_SCALE, self.win_offsets[i][0][1] * settings.WINDOW_SCALE)
        self.circle_radius = 0
        self.flag_to_delay = False
        self.flag_to_win_animation = False

    def set_pallete(self, level_name: str):
        path_to_file = \
            f'./map_levels/{self.ref_point_name}/{level_name}.omegapog_map_file_type_MLG_1337_228_100500_69_420'
        with open(path_to_file, mode='r', encoding='utf-8') as level_file:
            for line in level_file.readlines():
                parameters = line.strip().split(' ')
                self.current_palette = palette_manager.get_palette(
                    parameters[0])
                break

    def check_levels(self):
        _, _, all_map_matrix = parse_file('all_{}'.format(self.ref_point_name), 'map_levels/open_maps')
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text:
                            if len(all_map_matrix[i][j + 1]) >= 1 and all_map_matrix[i][j + 1][-1].name \
                                    in self.cursor.levels and self.matrix[i][j + 1][-1].name.split("_")[-1] == 'square':
                                self.matrix[i][j + 1].append(Object(j + 1, i, 1,
                                                                    all_map_matrix[i][j + 1][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette('default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i][j - 1]) >= 1 and all_map_matrix[i][j - 1][-1].name \
                                    in self.cursor.levels and self.matrix[i][j - 1][-1].name.split("_")[-1] == 'square':
                                self.matrix[i][j - 1].append(Object(j - 1, i, 1,
                                                                    all_map_matrix[i][j - 1][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette('default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i + 1][j]) >= 1 and all_map_matrix[i + 1][j][-1].name \
                                    in self.cursor.levels and self.matrix[i + 1][j][-1].name.split("_")[-1] == 'square':
                                self.matrix[i + 1][j].append(Object(j, i + 1, 1,
                                                                    all_map_matrix[i + 1][j][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette('default'),
                                                                    level_size=(32, 18)))
                            if len(all_map_matrix[i - 1][j]) >= 1 and all_map_matrix[i - 1][j][-1].name \
                                    in self.cursor.levels and self.matrix[i - 1][j][-1].name.split("_")[-1] == 'square':
                                self.matrix[i - 1][j].append(Object(j, i - 1, 1,
                                                                    all_map_matrix[i - 1][j][-1].name,
                                                                    True,
                                                                    palette=palette_manager.get_palette('default'),
                                                                    level_size=(32, 18)))
                            if self.matrix[i][j][-2].name.split('_')[0] in self.cursor.levels:
                                self.matrix[i][j].insert(-2, Object(j, i, 1,
                                                                    f'{self.matrix[i][j][-2].name.split("_")[0]}_n',
                                                                    True,
                                                                    palette=palette_manager.get_palette('default'),
                                                                    level_size=(32, 18)))
                                self.matrix[i][j].pop(-2)

                            if len(all_map_matrix[i - 1][j]) > 0 and len(self.matrix[i - 1][j]) == 0 \
                                    and all_map_matrix[i - 1][j][0].name.split("_")[0] == 'line' \
                                    or len(all_map_matrix[i + 1][j]) > 0 and len(self.matrix[i + 1][j]) == 0 \
                                    and all_map_matrix[i + 1][j][0].name.split("_")[0] == 'line' \
                                    or len(all_map_matrix[i][j - 1]) > 0 and len(self.matrix[i][j - 1]) == 0 \
                                    and all_map_matrix[i][j - 1][0].name.split("_")[0] == 'line' \
                                    or len(all_map_matrix[i][j + 1]) > 0 and len(self.matrix[i][j + 1]) == 0 \
                                    and all_map_matrix[i][j + 1][0].name.split("_")[0] == 'line':
                                for num in range(1, 4):
                                    try:
                                        _, _, part_matrix = parse_file(f'part_{self.ref_point_name}_{num}',
                                                                       f'map_levels/parts_of_map/{self.ref_point_name}')
                                        if len(part_matrix[i - 1][j]) > 0 and len(self.matrix[i - 1][j]) == 0 \
                                                and part_matrix[i - 1][j][0].name.split("_")[0] == 'line' \
                                                or len(part_matrix[i + 1][j]) > 0 and len(self.matrix[i + 1][j]) == 0 \
                                                and part_matrix[i + 1][j][0].name.split("_")[0] == 'line' \
                                                or len(part_matrix[i][j - 1]) > 0 and len(self.matrix[i][j - 1]) == 0 \
                                                and part_matrix[i][j - 1][0].name.split("_")[0] == 'line' \
                                                or len(part_matrix[i][j + 1]) > 0 and len(self.matrix[i][j + 1]) == 0 \
                                                and part_matrix[i][j + 1][0].name.split("_")[0] == 'line':
                                            for ix, linex in enumerate(part_matrix):
                                                for jx, cellx in enumerate(linex):
                                                    for _, rule_objectx in enumerate(cellx):
                                                        self.matrix[ix][jx].append(rule_objectx)
                                            self.first_iteration = True
                                    except FileNotFoundError:
                                        pass

        if self.complete_levels[self.ref_point_name] == 10:
            saves = map_saves()
            saves['reference_point'] += 1
            with open('./saves/map_saves', mode='w', encoding='utf-8') as file:
                for param in saves:
                    file.write(f'{param} {saves[param]}\n')
            self.flag_to_win_animation = True
        self.save()

    def text_to_png(self, text):
        if len(text) >= 32:
            x_offset = 0
        else:
            x_offset = (32 - len(text)) // 2
        text_in_objects = []

        for letter in text:
            if letter in settings.TEXT_ONLY:
                img_letter = Object(x_offset, 6, 1, letter,
                                    True, self.current_palette)
                text_in_objects.append(img_letter)
            x_offset += 1

        return text_in_objects

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
        for offset, radius in self.win_offsets:
            pygame.draw.circle(self.screen, self.current_palette.pixels[3][6],
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
            for character_object in self.text_to_png('area complete'):
                character_object.draw(text_surface)
            text_surface = pygame.transform.scale(
                text_surface, (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
            text_surface = text_surface.convert_alpha()
            self.screen.blit(text_surface, (0, 0))

        if self.win_offsets[0][1] >= max_radius and pygame.time.get_ticks() - self.delay >= 1000:
            for offset1 in border_offsets:
                pygame.draw.circle(
                    self.screen, self.current_palette.pixels[3][6], offset1, self.circle_radius)
            self.circle_radius += 8 * settings.WINDOW_SCALE
        if self.circle_radius >= 650 * settings.WINDOW_SCALE:
            self._state = State(GameState.BACK)

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
        Level Parsing. Adds objects to :attr:`~.Draw.matrix`.

        :param level_name: Name of the desired level
        :param path_to_level: Path to the desired level
        :raises OSError: If there's any problem opening the file.
        """
        self.level_palette, self.size, self.matrix = parse_file(level_name, path_to_file)

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
        elif x == self.size[1] - 1:
            neighbours[2] = [self.empty_object]

        if y == 0:
            neighbours[3] = [self.empty_object]
        elif y == self.size[0] - 1:
            neighbours[1] = [self.empty_object]

        for index, offset in enumerate(offsets):
            if neighbours[index] is None:
                neighbours[index] = self.matrix[x + offset[1]][y + offset[0]]
        return neighbours

    def save(self):
        string = f"{self.level_palette.name} {self.size[0]} {self.size[1]}\n"
        string_state, counter = unparse_all(self.matrix)
        if counter > 0:
            string += string_state
            with open(f"map_levels/{self.ref_point_name}"
                      f".omegapog_map_file_type_MLG_1337_228_100500_69_420", 'w',
                      encoding='utf-8') as file:
                file.write(string)

    def level_name(self):
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text and \
                                (self.matrix[i][j][-2].name.split('_')[0] in self.cursor.levels
                                 or self.matrix[i][j][-2].name.split('_')[0] == 'teeth'):
                            return self.matrix[i][j][-2].name.split('_')[0], i, j

    def go_to_game(self):
        for i, line in enumerate(self.matrix):
            for j, cell in enumerate(line):
                for k, rule_object in enumerate(cell):
                    if k < len(cell) and j < 31:
                        if rule_object.name == 'cursor' and not rule_object.is_text and \
                                self.matrix[i][j][-2].name.split('_')[0] in [*self.cursor.levels, 'teeth']:
                            if self.matrix[i][j][-2].name.split('_')[0] == 'teeth':
                                self._state = State(GameState.BACK)
                            elif len(self.matrix[i][j][-2].name.split('_')) == 1:
                                self._state = State(GameState.SWITCH, partial(PlayLevel,
                                                                              self.matrix[i][j][-2].name[0],
                                                                              f"map_levels/{self.ref_point_name}",
                                                                              False))
                            else:
                                self._state = State(GameState.SWITCH, partial(PlayLevel,
                                                                              self.matrix[i][j][-2].name[0],
                                                                              f"map_levels/{self.ref_point_name}",
                                                                              True))

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Draws and handles all events

        :param events: Events collected by the window
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Time between the current frame and the previous frame (unused, sadly)
        :type delta_time_in_milliseconds: int
        :return: Returns the state for proper game_context operation
        """
        map_surface = pygame.Surface((self.size[0] * 50, self.size[1] * 50))
        self._state = None
        saves = map_saves()
        if self.complete_levels[self.ref_point_name] != saves[self.ref_point_name]:
            self.complete_levels[self.ref_point_name] = saves[self.ref_point_name]
            self.check_levels()
        for event in events:
            if event.type == pygame.QUIT:
                self._state = State(GameState.BACK)
                self.save()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = State(GameState.BACK)
                    self.save()
                level_name = self.level_name()
                if event.key == pygame.K_RETURN and level_name is not None and \
                        level_name[0] in [*self.cursor.levels, 'teeth']:
                    self.delay = pygame.time.get_ticks()
                    if level_name[0] in self.cursor.levels:
                        try:
                            self.set_pallete(level_name[0])
                        except FileNotFoundError:
                            level_cell = self.matrix[level_name[1]][level_name[2]]
                            object_list = [i for i in level_cell if i.name.isdigit()]
                            assert len(object_list) == 1
                            level_object = object_list[0]
                            level_object.name = "error"
                            level_object.animation = level_object.animation_init()
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
        if self.flag_to_win_animation:
            self.win_animation()

        return self._state

    def on_init(self):
        sound_manager.load_music("sounds/Music/rain")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
