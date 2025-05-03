from typing import List, Optional, TYPE_CHECKING, Tuple
from math import ceil
from functools import partial

import pygame

import settings
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.palette import Palette
from classes.state import State
from elements.global_classes import palette_manager, language_manager, GuiSettings, GuiSettingsInactive
from classes.button import Button
from classes.objects import Object
from global_types import SURFACE
from elements.loader_util import parse_file

if TYPE_CHECKING:
    from elements.editor import Editor


class PaletteChoose(GameStrategy):
    def __init__(self, editor: "Editor", screen: SURFACE):
        super().__init__(screen)

        self.editor: "Editor" = editor
        self.cur_palette_name = editor.current_palette.name

        font = pygame.font.SysFont("Arial", int(72 * 2.5 * settings.WINDOW_SCALE))
        self._choose_palette_text = font.render(f"{language_manager['Choose a palette']}:", True, (255, 255, 255))

        self.test_matrix_size: Tuple[int, int]
        self.test_matrix: List[List[List[Object]]]
        self.test_matrix_size, self.test_matrix = self.get_test_matrix()

        self.apply_palette()

        self.buttons_page = 0
        self.buttons_page_count = 1
        self.batched_palette_buttons = self.build_batched_buttons(
            int(200 * settings.WINDOW_SCALE), self._choose_palette_text.get_height(), palette_manager.palettes
        )

        self.state = None
        self.back_button = Button(int(10 * settings.WINDOW_SCALE), int(10 * settings.WINDOW_SCALE),
                                  int(72 * settings.WINDOW_SCALE), int(72 * settings.WINDOW_SCALE),
                                  "white", GuiSettings(), "<", None)

        super().__init__(screen)

    @property
    def palette_button_width(self):
        return round(400 * settings.WINDOW_SCALE)

    @property
    def palette_button_height(self):
        return round(42 * settings.WINDOW_SCALE)

    @property
    def buttons_margin(self):
        return round(10 * settings.WINDOW_SCALE)

    @property
    def buttons_per_page(self):
        return round(settings.RESOLUTION[1] / (self.palette_button_height + 2 * self.buttons_margin) - 3)

    def dec_page(self):
        self.buttons_page -= 1
        self.buttons_page = max(0, self.buttons_page)

    def inc_page(self):
        self.buttons_page += 1
        self.buttons_page %= self.buttons_page_count

    def build_batched_buttons(self, x_offset: int, y_offset: int, palette_list: List[Palette]) -> List[List[Button]]:
        batched_buttons = []

        self.buttons_page_count = ceil(
            len(palette_list) / self.buttons_per_page)

        for i in range(0, len(palette_list), self.buttons_per_page):
            button_row = [self._create_palette_button(palette, y_offset, x_offset, index % self.buttons_per_page)
                          for index, palette in enumerate(palette_list[i:i + self.buttons_per_page])]

            # Button to previous page
            button_row.append(
                Button(
                    x=x_offset,
                    y=y_offset + self.buttons_per_page * (self.buttons_margin + self.palette_button_height),
                    width=round(self.palette_button_width / 2 - self.buttons_margin / 2),
                    height=self.palette_button_height,
                    outline="white" if i else "grey",
                    button_settings=GuiSettings() if i else GuiSettingsInactive(),
                    text=language_manager["prev page"],
                    action=self.dec_page if i else None,
                )
            )

            # Button to next page
            button_row.append(
                Button(
                    x=x_offset + round(self.palette_button_width / 2 - self.buttons_margin / 2) + self.buttons_margin,
                    y=y_offset + self.buttons_per_page *
                      (self.buttons_margin + self.palette_button_height),
                    width=round(self.palette_button_width / 2 - self.buttons_margin / 2),
                    height=self.palette_button_height,
                    outline="white" if (i / self.buttons_per_page) != self.buttons_page_count -
                                       1 else "grey",
                    button_settings=GuiSettings() if (i / self.buttons_per_page) != self.buttons_page_count -
                                                     1 else GuiSettingsInactive(),
                    text=language_manager["next page"],
                    action=self.inc_page if (i / self.buttons_per_page) != self.buttons_page_count - 1 else None,
                )
            )

            batched_buttons.append(button_row)

        return batched_buttons

    def _create_palette_button(self, palette: Palette, y_offset: int, x_offset: int, index: int) -> Button:
        return Button(
            x=x_offset,
            y=y_offset + (self.buttons_margin +
                          self.palette_button_height) * index,
            width=self.palette_button_width,
            height=self.palette_button_height,
            outline="grey" if palette.name == self.cur_palette_name else "white",
            button_settings=GuiSettings(
            ) if palette.name != self.cur_palette_name else GuiSettingsInactive(),
            text=language_manager[palette.name],
            action=partial(self.choose_palette, palette) if palette.name != self.cur_palette_name else None,
        )

    def choose_palette(self, palette):
        self.cur_palette_name = palette.name
        self.batched_palette_buttons = self.build_batched_buttons(
            int(200 * settings.WINDOW_SCALE), self._choose_palette_text.get_height(), palette_manager.palettes
        )

        self.editor.current_palette = palette
        self.editor.define_border_and_scale()
        if settings.DEBUG:
            print(f"chosen: {self.editor.current_palette.name}")

        self.apply_palette()

    def update_sticky_neighbours(self, game_object: Object):
        game_object.neighbours = self.get_neighbours(
            game_object.x, game_object.y)
        game_object.recursively_used = True
        neighbour_list: List[Object]
        for neighbour_list in game_object.neighbours:
            for neighbour in neighbour_list:
                if not neighbour.recursively_used:
                    self.update_sticky_neighbours(neighbour)
        game_object.animation = game_object.animation_init()
        game_object.moved = False

    def get_neighbours(self, y, x) -> List:
        """Looking for cell neighbours on top, right, bottom and left of the cell

        :param y: the y-axis coordinate on the matrix
        :type y: int
        :param x: the x-axis coordinate on the matrix
        :type x: int
        :return: Array with four neighbouring cells in the order top, right, bottom, left
        :rtype: List[]
        """

        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbours = [[] for _ in range(4)]
        empty_object = Object(-1, -1, 0, 'empty', False, self.editor.current_palette)

        if x == 0:
            neighbours[0] = [empty_object]
        elif x == self.test_matrix_size[1] - 1:
            neighbours[2] = [empty_object]

        if y == 0:
            neighbours[3] = [empty_object]
        elif y == self.test_matrix_size[0] - 1:
            neighbours[1] = [empty_object]

        for index, offset in enumerate(offsets):
            if not neighbours[index]:
                neighbours[index] = \
                    self.test_matrix[x + offset[1]][y + offset[0]]

        return neighbours

    def render_matrix(self) -> pygame.Surface:
        matrix_screen = pygame.Surface(
            (self.test_matrix_size[0] * 50, self.test_matrix_size[1] * 50))
        matrix_screen.fill(self.editor.current_palette.pixels[4][6])

        for line in self.test_matrix:
            for cell in line:
                for game_object in cell:
                    game_object.draw(matrix_screen, self.test_matrix)

        return matrix_screen

    def get_test_matrix(self) -> Tuple[Tuple[int, int], List[List[List[Object]]]]:
        _, self.test_matrix_size, self.test_matrix = parse_file("sample-level", "palettes")

        for line in self.test_matrix:
            for cell in line:
                for game_object in cell:
                    if game_object.name in settings.STICKY and not game_object.is_text:
                        self.update_sticky_neighbours(game_object)
        return self.test_matrix_size, self.test_matrix

    def apply_palette(self) -> None:
        for line in self.test_matrix:
            for cell in line:
                for object in cell:
                    object.palette = self.editor.current_palette
                    object.animation = object.animation_init()

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        self.state = State(GameState.FLIP)
        self.screen.fill('black')

        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or \
                    self.back_button.update(events):
                self.state = State(GameState.BACK)

        self.screen.blit(self._choose_palette_text, (92 * settings.WINDOW_SCALE, 0))

        self.back_button.draw(self.screen)
        for button in self.batched_palette_buttons[self.buttons_page]:
            button.draw(self.screen)
            button.update(events)

        self.screen.blit(
            pygame.transform.scale(
                self.render_matrix(),
                (((self.palette_button_height + self.buttons_margin)
                  * (self.buttons_per_page + 1),) * 2)
            ),
            ((self.palette_button_width + 400 * settings.WINDOW_SCALE),
             self._choose_palette_text.get_height()),
        )

        return self.state

    def on_init(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        if settings.DEBUG:
            print("QUIT and KEYDOWN")
