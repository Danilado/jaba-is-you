from datetime import datetime
from functools import partial
from math import ceil
from sys import exit
from typing import List, Optional

import pygame
# noinspection PyUnresolvedReferences
from jaba_speedup import copy_matrix

import settings
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.object_button import ObjectButton
from classes.objects import Object
from classes.palette import Palette
from classes.state import State
from elements.global_classes import EuiSettings, IuiSettings, sound_manager, palette_manager
from elements.overlay import EditorOverlay
from settings import OBJECTS, STICKY
from utils import settings_saves


def unparse_all(state):
    """Creating a line to save the grid state to a file in one write if it is not empty

    :param state: Three-dimensional grid state array
    :type state: list
    :return: Line for writing
    :rtype: str
    """
    string = ''
    counter = 0
    for row in state:
        for cell in row:
            for game_object in cell:
                counter += 1
                string += game_object.unparse() + '\n'
    return string, counter


def direction_to_unicode(direction: int) -> str:
    """
    Directions to Unicode Arrows

    :param direction:
        0 - Up
        1 - Right
        2 - Down
        3 - Left
    :return: One symbol - Unicode Arrow
    """
    return '↑' if direction == 0 else '→' if direction == 1 else '↓' if direction == 2 else '←'


class Editor(GameStrategy):
    """Level editor class

    :param GameStrategy: It is a game strategy and is inherited from the corresponding class
    """

    def __init__(self, screen: pygame.Surface):
        """Level editor constructor

        :param screen: Window for drawing
        :type screen: pygame.Surface
        """
        super().__init__(screen)
        # overlay related
        self.exit_flag = False
        self.show_grid = settings_saves()[0]
        self.discard = False
        self.level_name = None
        self.state = None
        self.first_iteration = True
        self.new_loaded = False
        # tools
        self.tool = 1
        self.direction = 1
        self.is_text = False
        self.name: Optional[str] = None
        self.direction_key_map = {
            0: 1,
            1: 0,
            2: 3,
            3: 2,
        }
        # history
        self.changes: List[List[List[List[Object]]]] = []
        # matrix state
        self.current_state: List[List[List[Object]]] = [
            [[] for _ in range(32)] for _ in range(18)]
        # focused cell
        self.focus = (-1, -1)
        self.search_text = ''
        self.filter = ''
        self.text_timestamp = pygame.time.get_ticks() + 255
        self.font = pygame.font.SysFont(
            'notosans', int(300 * settings.WINDOW_SCALE))
        # buttons
        self.buttons: List[ObjectButton] = []
        self.page = 0
        self.pagination_limit = ceil(len(OBJECTS) / 12)
        self.pagination_buttons = [
            Button(settings.RESOLUTION[0] + int(17 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(222 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(20 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   "<", partial(self.page_turn, -1)),
            Button(settings.RESOLUTION[0] + int(101 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(222 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(20 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   ">", partial(self.page_turn, 1)),
        ]
        # metadata
        self._current_palette: Palette = palette_manager.get_palette("default")
        self.size = (32, 18)
        self.scale = 1
        self.window_offset: List[int] = [0, 0]
        self.border_screen: pygame.Surface = None
        # features
        self.screen = pygame.display.set_mode(
            (1800 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
        self.page_turn(0)
        self.empty_object = Object(-1, -1, 0, 'empty',
                                   is_text=False, palette=self.current_palette)

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
                self.window_offset[1] = (1600 - self.size[0]*50*self.scale)/2
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
                self.window_offset[0] = (900 - self.size[1]*50*self.scale)/2
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

    def save(self, state, name=None):
        """Saving a 3D array to disc

        :param state: Three-dimensional grid state array
        :type state: list
        """
        string = f"{self.current_palette.name} {self.size[0]} {self.size[1]}\n"
        string_state, counter = unparse_all(state)
        if counter > 0:
            string += string_state
            if name is None:
                name = 'autosave_' + datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
            with open(f"levels/{name}.omegapog_map_file_type_MLG_1337_228_100500_69_420", 'w',
                      encoding='utf-8') as file:
                file.write(string)

    def page_turn(self, number: int):
        """Changes the object list page

        :param number: Forward or backward flip and how many pages
        :type number: int
        """
        if self.filter == '':
            self.pagination_limit = ceil(len(OBJECTS) / 12)
        self.page = (self.page + number) % self.pagination_limit
        self.buttons = self.parse_buttons()

    def parse_buttons(self):
        """
        Gives a list of 12 or fewer buttons located on the buttons (?) page,
        where the editor is currently located

        :return: button array
        :rtype: list
        """
        filtered_array = []
        for game_object in OBJECTS:
            if self.filter in game_object:
                filtered_array.append(game_object)
        self.pagination_limit = max(ceil(len(filtered_array) / 12), 1)
        button_objects_array = filtered_array[12 *
                                              self.page:12 * (self.page + 1)]
        button_array = []
        for index, text in enumerate(button_objects_array):
            button_array.append(
                ObjectButton(x=int(settings.RESOLUTION[0] + (28 + 84 * (index % 2)) * settings.WINDOW_SCALE),
                             y=int((25 + 55 * (index - index % 2))
                                   * settings.WINDOW_SCALE),
                             width=int(50 * settings.WINDOW_SCALE),
                             height=int(50 * settings.WINDOW_SCALE), outline=(0, 0, 0),
                             button_settings=EuiSettings(), text=text, action=partial(self.set_name, text),
                             is_text=self.is_text, direction=self.direction, movement_state=0,
                             palette=self.current_palette))
        return button_array

    def unresize(self):
        """Changes the screen resolution from extended to original via the magic constants 1600x900"""
        self.screen = pygame.display.set_mode(
            (1600 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))

    def safe_exit(self):
        """Prepare to safely exit the editor without losing changes"""
        self.save(self.current_state, self.level_name)
        self.unresize()

    def extreme_exit(self):
        """Prepare to safely exit the editor without losing changes"""
        self.save(self.current_state, None)
        self.unresize()

    def set_name(self, string: str):
        """Changing the name of the object, and therefore the textures and rules.

        :param string: New object name
        :type string: str
        """
        self.name = string

    def turn(self, direction: int):
        """Rotate object

        :param direction: direction where 1 - clockwise and -1 anti-clockwise
        """
        self.direction = (self.direction - direction) % 4
        self.page_turn(0)

    def set_tool(self, number: int):
        """Tool change

        :param number:
            [0 - 2] where 0 - remove, 1 - create and 2 - investigate the cell and output the contents to the console
        :type number: int
        """
        self.tool = number

    def is_text_swap(self):
        """Changes whether the object is text or not"""
        self.is_text = not self.is_text
        self.page_turn(0)

    def undo(self):
        """Undoes the last change"""
        if len(self.changes) != 0:
            self.current_state = self.changes[-1]
            self.changes.pop()
            for line in self.current_state:
                for cell in line:
                    for game_object in cell:
                        if game_object.name in STICKY and not game_object.is_text:
                            neighbours = self.get_neighbours(
                                game_object.x, game_object.y)
                            game_object.neighbours = neighbours
                            game_object.animation = game_object.animation_init()

    def get_neighbours(self, y, x) -> List[Object]:
        """Looking for cage neighbours above, right, below and left

        :param y: y-axis coordinate on the matrix
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
        neighbours = [[] for _ in range(4)]
        if x == 0:
            neighbours[0] = [self.empty_object]
        elif x == settings.RESOLUTION[1] // int(50 * settings.WINDOW_SCALE) - 1:
            neighbours[2] = [self.empty_object]

        if y == 0:
            neighbours[3] = [self.empty_object]
        elif y == settings.RESOLUTION[0] // int(50 * settings.WINDOW_SCALE) - 1:
            neighbours[1] = [self.empty_object]

        for index, offset in enumerate(offsets):
            if neighbours[index] is None:
                neighbours[index] = self.current_state[x +
                                                       offset[1]][y + offset[0]]
        return neighbours

    def create(self):
        """
        If there is no object with the same name in the selected cell, creates it there and
        writes the previous grid state to the archive array
        """
        if self.name is not None:
            flag = 0
            for game_object in self.current_state[self.focus[1]][self.focus[0]]:
                if game_object.name == self.name:
                    flag = 1
                    break
            if not flag:
                neighbours = []
                if self.name in STICKY and not self.is_text:
                    # THIS SHOULD BE DONE BEFORE ADDING IT TO THE MATRIX
                    neighbours = self.get_neighbours(
                        self.focus[0], self.focus[1])
                self.changes.append(copy_matrix(self.current_state))
                self.current_state[self.focus[1]][self.focus[0]].append(
                    Object(x=self.focus[0], y=self.focus[1], direction=self.direction, name=self.name,
                           is_text=self.is_text, movement_state=0, neighbours=neighbours, palette=self.current_palette))
                if self.name in STICKY and not self.is_text:
                    # THIS SHOULD BE DONE AFTER ADDING AN OBJECT TO THE MATRIX
                    for array in neighbours:
                        for neighbour in array:
                            if neighbour.name in STICKY and not neighbour.is_text:
                                neighbour.neighbours = self.get_neighbours(
                                    neighbour.x, neighbour.y)
                                neighbour.animation = neighbour.animation_init()

    def delete(self):
        """If there are objects in the cell, deletes the last object created from them"""
        # ? Is it necessary to choose what to remove?
        if len(self.current_state[self.focus[1]][self.focus[0]]) > 0:
            self.changes.append(copy_matrix(self.current_state))
            self.current_state[self.focus[1]][self.focus[0]].pop()
            neighbours = self.get_neighbours(
                self.focus[0], self.focus[1])
            for array in neighbours:
                for neighbour in array:
                    if neighbour.name in STICKY and not neighbour.is_text:
                        neighbour.neighbours = self.get_neighbours(
                            neighbour.x, neighbour.y)
                        neighbour.animation = neighbour.animation_init()

    def pickup(self):
        if len(self.current_state[self.focus[1]][self.focus[0]]) > 0:
            self.name = self.current_state[self.focus[1]
                                           ][self.focus[0]][-1].name
            self.is_text = self.current_state[self.focus[1]
                                              ][self.focus[0]][-1].is_text

    def overlay(self):
        """Opens the editor's control menu"""
        self.unresize()
        self.state = State(GameState.SWITCH, partial(EditorOverlay, self))

    @property
    def current_palette(self) -> Palette:
        return self._current_palette

    @current_palette.setter
    def current_palette(self, value: Palette):
        self._current_palette = value
        self.buttons = self.parse_buttons()
        for state in self.changes + [self.current_state]:
            for line in state:
                for cell in line:
                    for rule_object in cell:
                        rule_object.palette = value
                        rule_object.animation = rule_object.animation_init()

    def update_text(self):
        self.page = 0
        self.filter = self.search_text
        self.page_turn(0)
        self.text_timestamp = pygame.time.get_ticks()

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Draws the editor (including all its elements) and handles all user actions

        :param events: Events collected by the window
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Time between the current frame and the previous frame (unused, sadly)
        :type delta_time_in_milliseconds: int
        :return: Returns the state for proper game_context operation
        :rtype: Optional[State]
        """

        self.state = None
        if self.first_iteration:
            self.first_iteration = False
            self.overlay()
        if self.exit_flag:
            if not self.discard:
                self.safe_exit()
            self.state = State(GameState.BACK)
            self.unresize()
        if self.new_loaded:
            self.changes.clear()
            self.new_loaded = False
            for line in self.current_state:
                for cell in line:
                    for game_object in cell:
                        if game_object.name in STICKY and not game_object.is_text:
                            neighbours = self.get_neighbours(
                                game_object.x, game_object.y)
                            game_object.neighbours = neighbours
                            game_object.animation = game_object.animation_init()

        self.screen.fill(self.current_palette.pixels[4][6])
        for event in events:
            event: pygame.event.Event
            if event.type == pygame.QUIT:
                self.extreme_exit()
                self.state = State(GameState.BACK)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.overlay()
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if event.key == pygame.K_BACKSPACE:
                        self.search_text = ''
                        self.update_text()
                    if event.key == pygame.K_e:
                        self.turn(-1)
                    if event.key == pygame.K_q:
                        self.turn(1)
                    if event.key == pygame.K_t:
                        self.is_text_swap()
                    if event.key == pygame.K_x:
                        self.set_tool(0)
                    if event.key == pygame.K_c:
                        self.set_tool(1)
                    if event.key == pygame.K_v:
                        self.set_tool(2)
                    if event.key == pygame.K_a:
                        self.page_turn(-1)
                    if event.key == pygame.K_d:
                        self.page_turn(1)
                    if event.key == pygame.K_z:
                        self.undo()
                elif len(pygame.key.name(event.key)) == 1:
                    self.search_text += pygame.key.name(event.key)
                    self.update_text()
                elif event.key == pygame.K_BACKSPACE and self.search_text != '':
                    self.search_text = self.search_text.rstrip(
                        self.search_text[-1])
                    self.update_text()

            if event.type == pygame.MOUSEMOTION:
                if event.pos[0] - self.window_offset[1] <= self.size[0]*50*self.scale*settings.WINDOW_SCALE:
                    if event.pos[1] - self.window_offset[0] <= self.size[1]*50*self.scale*settings.WINDOW_SCALE:
                        self.focus = (int((event.pos[0] - self.window_offset[1]) //
                                      (50*settings.WINDOW_SCALE*self.scale)),
                                      int((event.pos[1] - self.window_offset[0]) //
                                      (50*settings.WINDOW_SCALE*self.scale)))
                        # NOTE MIGHT BE BETTER TO DIVIDE IT BY SCALE.
                else:
                    self.focus = (-1, -1)
            if event.type == pygame.MOUSEBUTTONDOWN or (pygame.key.get_mods() & pygame.KMOD_SHIFT and pygame.mouse.get_pressed()[0]):
                if self.focus[0] != -1:
                    if self.tool == 1:
                        self.create()
                    elif self.tool == 0:
                        self.delete()
                    else:
                        self.pickup()

        indicators = [
            Button(settings.RESOLUTION[0] + int(17 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(192 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(75 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   f"Obj\n{self.name}"),
            Button(settings.RESOLUTION[0] + int(101 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(192 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(75 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   f"Text\n{'True' if self.is_text else 'False'}", self.is_text_swap),
            Button(settings.RESOLUTION[0] + int(17 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(100 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(75 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   f"Tool\n{'Create' if self.tool == 1 else 'Delete' if self.tool == 0 else 'Pickup'}",
                   partial(self.set_tool, 0 if self.tool == 1 else 1 if self.tool == 2 else 2)),
            Button(settings.RESOLUTION[0] + int(101 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] - int(100 * settings.WINDOW_SCALE),
                   int(75 * settings.WINDOW_SCALE), int(75 *
                                                        settings.WINDOW_SCALE), (0, 0, 0), IuiSettings(),
                   f"Dir\n{direction_to_unicode(self.direction)}",
                   partial(self.turn, -1)),
        ]

        matrix_screen = pygame.Surface((self.size[0]*50, self.size[1]*50))
        matrix_screen.fill(self.current_palette.pixels[4][6])

        pygame.draw.rect(matrix_screen, (44, 44, 44),
                         (self.focus[0] * 50, self.focus[1] * 50, 50, 50))

        if self.show_grid:
            for x in range(0, self.size[0] * 50, 50):
                for y in range(0, self.size[1] * 50, 50):
                    pygame.draw.rect(
                        matrix_screen, (255, 255, 255), (x, y, 50, 50), 1)

        for line in self.current_state:
            for cell in line:
                for game_object in cell:
                    game_object.draw(matrix_screen)

        self.screen.blit(pygame.transform.scale(
            matrix_screen, (self.size[0] * 50 * self.scale * settings.WINDOW_SCALE,
                            self.size[1] * 50 * self.scale * settings.WINDOW_SCALE)),
                         (self.window_offset[1] * settings.WINDOW_SCALE,
                             self.window_offset[0] * settings.WINDOW_SCALE))
        if self.border_screen:
            self.screen.blit(self.border_screen, (0, 0))

        for button in self.buttons:
            if self.state is None and button.update(events) and button.action is exit:
                break
            button.draw(self.screen)

        for pagination_button in self.pagination_buttons:
            pagination_button.update(events)
            pagination_button.draw(self.screen)

        for indicator in indicators:
            indicator.update(events)
            indicator.draw(self.screen)

        if pygame.time.get_ticks() - self.text_timestamp < 510:
            text = self.font.render(self.search_text, False, (255,)*3)
            text.set_alpha(
                255 - (pygame.time.get_ticks() - self.text_timestamp)//2)
            self.screen.blit(text, (800 * settings.WINDOW_SCALE - text.get_width() /
                             2, 450 * settings.WINDOW_SCALE - text.get_height() / 2))

        if pygame.time.get_ticks() - self.text_timestamp > 1000:
            self.search_text = ''

        if self.state is None:
            self.state = State(GameState.FLIP)
        return self.state

    def on_init(self):
        sound_manager.load_music("sounds/Music/editor")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
