from typing import List, Optional

import pygame

import settings
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from elements.editor import Editor
from elements.global_classes import GuiSettings, sound_manager, sprite_manager, language_manager
from elements.level_loader import Loader
from elements.global_classes import GuiSettings, sound_manager, sprite_manager
from elements.map_menu import MapMenu
from elements.settings_menu import SettingsMenu
from global_types import SURFACE


class MainMenu(GameStrategy):
    """
    Main menu strategy
    """

    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self.screen.set_alpha(None)
        self._state: Optional[State] = None

    def _start_the_game(self):
        self._state = State(GameState.SWITCH, MapMenu)

    def _go_to_editor(self):
        self._state = State(GameState.SWITCH, Editor)

    def _exit_the_game(self):
        self._state = State(GameState.STOP, None)

    def _go_to_loader(self):
        self._state = State(GameState.SWITCH, Loader)

    def _go_to_options(self):
        self._state = State(GameState.SWITCH, SettingsMenu)

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int):
        centered_x = settings.RESOLUTION[0] // 2 - int(200 * settings.WINDOW_SCALE)
        centered_y = settings.RESOLUTION[1] // 2
        buttons = [
            Button(centered_x,
                   centered_y - int(60 * settings.WINDOW_SCALE), int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(), language_manager['Start game'],
                   self._start_the_game),
            Button(centered_x, centered_y,
                   int(400 * settings.WINDOW_SCALE), int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),
                   language_manager['Level Editor'], self._go_to_editor),
            Button(centered_x,
                   centered_y + int(60 * settings.WINDOW_SCALE), int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(), language_manager['Levels'],
                   self._go_to_loader),
            Button(centered_x,
                   centered_y + int(120 * settings.WINDOW_SCALE), int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(),language_manager['Settings'],
                   self._go_to_options),
            Button(centered_x,
                   centered_y + int(180 * settings.WINDOW_SCALE), int(400 * settings.WINDOW_SCALE),
                   int(50 * settings.WINDOW_SCALE), (0, 0, 0), GuiSettings(), language_manager['Exit'],
                   self._exit_the_game)
        ]
        self._state = None

        self.screen.fill("black")

        for event in events:
            if event.type == pygame.QUIT:
                self._exit_the_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._exit_the_game()
        for button in buttons:
            button.draw(self.screen)
            button.update(events)
        if self._state is None:
            self._state = State(GameState.FLIP, None)
        else:
            pygame.event.set_allowed(None)

        self.screen.blit(sprite_manager.get("./jaba_is_logo.png", size=(400*settings.WINDOW_SCALE,)*2),
                         (settings.RESOLUTION[0]//2 - 200*settings.WINDOW_SCALE, 0))

        return self._state

    def on_init(self):
        sound_manager.load_music("sounds/Music/menu")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        pygame.event.set_allowed(
            [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP])
        if settings.DEBUG:
            print("QUIT, KEYDOWN, MOUSEBUTTONUP")
