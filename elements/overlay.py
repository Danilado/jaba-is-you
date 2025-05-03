from functools import partial
from typing import List, Optional, TYPE_CHECKING

import pygame

import settings
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.input import Input
from classes.state import State
from elements.global_classes import GuiSettings, EuiSettings, language_manager
from elements.level_loader import Loader
from elements.palette_choose import PaletteChoose

if TYPE_CHECKING:
    from elements.editor import Editor


class EditorOverlay(GameStrategy):
    """
    Level editor control overlay
    """

    def on_init(self):
        pygame.event.set_allowed(
            [pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONUP])
        if settings.DEBUG:
            print("QUIT KEYDOWN KEYUP MOUSEBUTTONUP")

    def __init__(self, editor: "Editor", screen: pygame.Surface):
        """Initialises the overlay

        :param screen: Which surface to draw on
        :param editor: An instance of the Editor class, which manages the overlay
        """
        super().__init__(screen)
        self.state: Optional[State] = None
        self.editor: "Editor" = editor
        self.loaded_flag = False
        self.label = self.editor.level_name
        if self.label is None:
            self.label = language_manager['New level']
        self.buttons = [
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 -
                   int(280 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE), int(50 *
                                                         settings.WINDOW_SCALE), (0, 0, 0), EuiSettings(),
                   f"{language_manager['You change']} {self.label}"),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 -
                   int(120 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   language_manager['Back'],
                   self.cancel),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 -
                   int(60 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   language_manager['Load level'],
                   self.load),
            Input(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE), settings.RESOLUTION[1] // 2,
                  int(400 * settings.WINDOW_SCALE),
                  int(50 * settings.WINDOW_SCALE), (255, 255, 255), EuiSettings(), language_manager['New name']),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 +
                   int(60 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   f"{language_manager['Save']}",
                   self.save),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 +
                   int(120 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   f"{language_manager['Save and exit']}",
                   self.force_exit),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 +
                   int(180 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   f"{language_manager['Exit without saving']}",
                   self.hard_force_exit),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 -
                   int(230 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), EuiSettings()),
            Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                   settings.RESOLUTION[1] // 2 -
                   int(180 * settings.WINDOW_SCALE),
                   int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   f"{language_manager['Change palette']}",
                   self.switch_to_palette_choose),
            Button(settings.RESOLUTION[0] - 150,
                   int(100 * settings.WINDOW_SCALE), int(50 *
                                                         settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   "<",
                   partial(self.resize, 0, -1)),
            Button(settings.RESOLUTION[0] - 150,
                   int(175 * settings.WINDOW_SCALE), int(50 *
                                                         settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   "<",
                   partial(self.resize, 1, -1)),
            Button(settings.RESOLUTION[0] - 50,
                   int(100 * settings.WINDOW_SCALE), int(50 *
                                                         settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   ">",
                   partial(self.resize, 0, 1)),
            Button(settings.RESOLUTION[0] - 50,
                   int(175 * settings.WINDOW_SCALE), int(50 *
                                                         settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   ">",
                   partial(self.resize, 1, 1)),
        ]

    def resize(self, axe, amount):
        if not axe:
            if self.editor.size[0] + amount in range(4, 33):
                self.editor.size = (
                    self.editor.size[0] + amount, self.editor.size[1])
        else:
            if self.editor.size[1] + amount in range(4, 19):
                self.editor.size = (
                    self.editor.size[0], self.editor.size[1] + amount)
        self.editor.define_border_and_scale()

    def save(self):
        """Saves the editor matrix
        """
        self.editor.safe_exit()

    def cancel(self):
        """Cancels entry to the overlay and returns to the editor
        """
        self.state = State(GameState.BACK)

    def load(self):
        """
        Makes automatic saving changes to the editor, if any, and calls the loader to load the level into the editor
        """
        self.editor.extreme_exit()
        self.state = State(GameState.SWITCH, partial(Loader, from_editor_overlay=self))

    def force_exit(self):
        """Exits the editor with saving"""
        self.state = State(GameState.BACK)
        self.editor.exit_flag = True

    def hard_force_exit(self):
        """Exits without saving"""
        self.state = State(GameState.BACK)
        self.editor.exit_flag = True
        self.editor.discard = True

    def switch_to_palette_choose(self):
        self.state = State(GameState.SWITCH, partial(
            PaletteChoose, self.editor))

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Draws the editor control overlay and handles events

        :param events: Events collected by the window
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Time between the current frame and the previous frame (unused, sadly)
        :type delta_time_in_milliseconds: int
        :return: state for proper game_context operation
        """
        self.state = State(GameState.BACK) if self.loaded_flag else None
        self.editor.new_loaded = bool(self.loaded_flag)
        self.buttons[7].text = f"{language_manager['current palette']}: {self.editor.current_palette.name}"
        self.screen.fill('black')

        for event in events:
            if event.type == pygame.QUIT:
                self.state = State(GameState.BACK)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.editor.level_name = str(self.buttons[3])
                self.editor.define_border_and_scale()
                self.state = State(GameState.BACK)
            if event.type == pygame.KEYUP:
                if str(self.buttons[3]):
                    self.label = str(self.buttons[3])
                self.buttons[0] = Button(settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE),
                                         settings.RESOLUTION[1] // 2 -
                                         int(280 * settings.WINDOW_SCALE),
                                         int(400 * settings.WINDOW_SCALE),
                                         int(50 * settings.WINDOW_SCALE), (0, 0, 0),
                                         EuiSettings(), f"{language_manager['You change']} {self.label}")

        for button in self.buttons:
            button.update(events)
            button.draw(self.screen)

        axis = [Button(settings.RESOLUTION[0] - 100,
                       int(100 * settings.WINDOW_SCALE), int(50 *
                                                             settings.WINDOW_SCALE),
                       int(50 * settings.WINDOW_SCALE), (0, 0, 0), EuiSettings(),
                       f"{self.editor.size[0]}"),
                Button(settings.RESOLUTION[0] - 100,
                       int(175 * settings.WINDOW_SCALE), int(50 *
                                                             settings.WINDOW_SCALE),
                       int(50 * settings.WINDOW_SCALE), (0, 0, 0), EuiSettings(),
                       f"{self.editor.size[1]}"), ]
        for axe in axis:
            axe.draw(self.screen)

        if self.state is not None:
            if str(self.buttons[3]) != '':
                self.editor.level_name = str(self.buttons[3])
                if self.editor.level_name == '':
                    self.editor.level_name = None
            self.screen = pygame.display.set_mode(
                (1800 * settings.WINDOW_SCALE, 900 * settings.WINDOW_SCALE))
        if self.state is None:
            self.state = State(GameState.FLIP)
        return self.state
