from typing import List, Optional

import pygame

import settings
from classes.slider import Slider
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from elements.global_classes import GuiSettings, language_manager
from global_types import SURFACE
from utils import settings_saves


class SettingsMenu(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self.flag_to_move_circle = False
        self._state: Optional[State] = None
        self.options = settings_saves()

        x = int(settings.RESOLUTION[0] // 2 + (200 + 400 *
                pygame.mixer.music.get_volume()) * settings.WINDOW_SCALE)
        y = int(settings.RESOLUTION[1] // 2 - 300 *
                settings.WINDOW_SCALE + 3 * settings.WINDOW_SCALE)
        self.circle_music = [x, y]

        self.slider = Slider(settings.RESOLUTION[0] // 2 + 200 * settings.WINDOW_SCALE,
                             settings.RESOLUTION[1] // 2 -
                             300 * settings.WINDOW_SCALE,
                             400 * settings.WINDOW_SCALE, 6 *
                             settings.WINDOW_SCALE, (255, 255, 255),
                             self.circle_music, 5, (80, 80, 80), self.set_music_volume)
        self.buttons: List[Optional[Button]] = [None,]*5
        self.reset_buttons()

    def set_resolution_800x450(self):
        settings.WINDOW_SCALE = 0.5
        settings.RESOLUTION = [800, 450]
        self.screen = pygame.display.set_mode(settings.RESOLUTION)
        self.options[3] = 1
        self.options[4] = 0.5
        x = int(settings.RESOLUTION[0] // 2 + (200 + 400 *
                pygame.mixer.music.get_volume()) * settings.WINDOW_SCALE)
        y = int(settings.RESOLUTION[1] // 2 - 300 *
                settings.WINDOW_SCALE + 3 * settings.WINDOW_SCALE)
        self.circle_music = [x, y]
        self.slider = Slider(settings.RESOLUTION[0] // 2 + 200 * settings.WINDOW_SCALE,
                             settings.RESOLUTION[1] // 2 -
                             300 * settings.WINDOW_SCALE,
                             400 * settings.WINDOW_SCALE, 6 *
                             settings.WINDOW_SCALE, (255, 255, 255),
                             self.circle_music, 5, (80, 80, 80), self.set_music_volume)

    def set_resolution_1600x900(self):
        settings.WINDOW_SCALE = 1.0
        settings.RESOLUTION = [1600, 900]
        self.screen = pygame.display.set_mode(settings.RESOLUTION)
        self.options[3] = 0
        self.options[4] = 1
        x = int(settings.RESOLUTION[0] // 2 + (200 + 400 *
                pygame.mixer.music.get_volume()) * settings.WINDOW_SCALE)
        y = int(settings.RESOLUTION[1] // 2 - 300 *
                settings.WINDOW_SCALE + 3 * settings.WINDOW_SCALE)
        self.circle_music = [x, y]
        self.slider = Slider(settings.RESOLUTION[0] // 2 + 200 * settings.WINDOW_SCALE,
                             settings.RESOLUTION[1] // 2 -
                             300 * settings.WINDOW_SCALE,
                             400 * settings.WINDOW_SCALE, 6 *
                             settings.WINDOW_SCALE, (255, 255, 255),
                             self.circle_music, 5, (80, 80, 80), self.set_music_volume)

    def save_file(self):
        with open('saves/option_settings', mode='w', encoding='utf-8') as file:
            for _, param in enumerate(self.options):
                file.write(f'{param}\n')
            file.close()

    def go_back(self):
        """exit to previous menu"""
        self.save_file()
        self._state = State(GameState.BACK)

    def set_language(self):
        current_language_index = language_manager.available_languages.index(self.options[1])

        # Most likely this code can be shortened to `new_index = current_language_index + 1 % len(
        # language_manager.available_languages)` but I can't make it work. :(
        new_index = current_language_index + 1
        if new_index >= len(language_manager.available_languages):
            new_index = 0

        self.options[1] = language_manager.available_languages[new_index]
        language_manager.current_language = self.options[1]

    def set_show_grid(self):
        self.options[0] = not self.options[0]

    def set_music_volume(self):
        if pygame.mouse.get_pos()[0] > settings.RESOLUTION[0] // 2 + 200 * settings.WINDOW_SCALE:
            if settings.RESOLUTION[0] // 2 + (200 + 400) * settings.WINDOW_SCALE > pygame.mouse.get_pos()[0]:
                self.circle_music[0] = int(pygame.mouse.get_pos()[0])
            else:
                self.circle_music[0] = settings.RESOLUTION[0] // 2 + \
                    (200 + 400) * settings.WINDOW_SCALE
        else:
            self.circle_music[0] = settings.RESOLUTION[0] // 2 + \
                200 * settings.WINDOW_SCALE
        pygame.mixer.music.set_volume(
            (self.circle_music[0] - (settings.RESOLUTION[0] // 2 + 200 * settings.WINDOW_SCALE)) / 400)
        self.options[2] = pygame.mixer.music.get_volume()

    def reset_buttons(self):
        grid_status = 'on' if self.options[0] else 'off'
        self.buttons[0] = Button(settings.RESOLUTION[0] // 2 - int(600 * settings.WINDOW_SCALE),
                                 settings.RESOLUTION[1] // 2 -
                                 int(180 * settings.WINDOW_SCALE),
                                 int(1200 * settings.WINDOW_SCALE),
                                 int(50 * settings.WINDOW_SCALE), (0, 0, 0),
                                 GuiSettings(), language_manager[f'Turn {grid_status} grid'], self.set_show_grid)

        self.buttons[1] = Button(settings.RESOLUTION[0] // 2 - int(600 * settings.WINDOW_SCALE),
                                 settings.RESOLUTION[1] // 2 -
                                 int(120 * settings.WINDOW_SCALE),
                                 int(1200 * settings.WINDOW_SCALE), int(50 *
                                                                        settings.WINDOW_SCALE), (0, 0, 0),
                                 GuiSettings(), f"Language: {language_manager['Language']}", self.set_language)
        self.buttons[2] = Button(settings.RESOLUTION[0] // 2 - int(600 * settings.WINDOW_SCALE),
                                 settings.RESOLUTION[1] // 2,
                                 int(1200 * settings.WINDOW_SCALE), int(50 *
                                                                        settings.WINDOW_SCALE), (0, 0, 0),
                                 GuiSettings(), language_manager["Back"], self.go_back)

        self.buttons[3] = Button(settings.RESOLUTION[0] // 2 - int(600 * settings.WINDOW_SCALE),
                                 settings.RESOLUTION[1] // 2 -
                                 int(60 * settings.WINDOW_SCALE),
                                 int(575 * settings.WINDOW_SCALE),
                                 int(50 * settings.WINDOW_SCALE), (0, 0, 0),
                                 GuiSettings(), "800x450", self.set_resolution_800x450)
        self.buttons[4] = Button(settings.RESOLUTION[0] // 2 + int(25 * settings.WINDOW_SCALE),
                                 settings.RESOLUTION[1] // 2 -
                                 int(60 * settings.WINDOW_SCALE),
                                 int(575 * settings.WINDOW_SCALE),
                                 int(50 * settings.WINDOW_SCALE), (0, 0, 0),
                                 GuiSettings(), "1600x900", self.set_resolution_1600x900)

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Draws the loader interface and handles all events

        :param events: Events collected by the window
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Time between the current frame and the previous frame (unused)
        :type delta_time_in_milliseconds: int
        :return: Returns the state for proper game_context operation
        """
        self.screen.fill("black")
        self._state = None
        if events:
            font = pygame.font.Font(
                'fonts/ConsolateElf.ttf', int(20 * settings.WINDOW_SCALE))
            text = language_manager['Music volume']
            text_surface = font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (
                settings.RESOLUTION[0] // 2 +
                (200 - 14 * len(text)) * settings.WINDOW_SCALE,
                settings.RESOLUTION[1] // 2 + (-300 - 15) * settings.WINDOW_SCALE))
            for event in events:
                if event.type == pygame.QUIT:
                    self._state = State(GameState.BACK)
                    self.save_file()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.save_file()
                    self._state = State(GameState.BACK)
            self.reset_buttons()
            self.slider.update(events)
            self.slider.draw(self.screen)
            for button in self.buttons:
                button.draw(self.screen)
                button.update(events)
            if self._state is None:
                self._state = State(GameState.FLIP, None)
        return self._state

    def on_init(self):
        ...
