import time
from typing import List, Optional

import pygame.font

from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.progressbar import ProgressBar
from classes.state import State
from elements.global_classes import sound_manager
from elements.main_menu import MainMenu
from global_types import SURFACE


class ProgressBarMenu(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        if not sound_manager.thread_done:
            while sound_manager.content_length is None:
                # Wait for other threads to load content_length
                time.sleep(0.1)
            assert sound_manager.content_length is not None   # Pycharm is stupid
            self.progress_bar = ProgressBar(0, 90,
                                            screen.get_width(), screen.get_height() // 4,

                                            border_color="lightgreen",
                                            left_right_border_size=self.screen.get_width()//384,
                                            up_down_border_size=self.screen.get_height()//216,

                                            progress_color="darkgreen", progress_min=0.0,
                                            progress_max=float(sound_manager.content_length),

                                            progress_background_color="green")
            font = pygame.font.Font("fonts/ConsolateElf.ttf", 84)
            self.loading_text = font.render("beep-boop. downloading files.", True, (255,)*3)

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        if sound_manager.thread_done:
            return State(GameState.SWITCH, MainMenu)
        assert sound_manager.content_bytes_downloaded is not None
        for event in events:
            if event.type == pygame.QUIT:
                return State(GameState.STOP)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return State(GameState.STOP)
        self.progress_bar.progress = float(sound_manager.content_bytes_downloaded)
        if self.progress_bar.draw(self.screen):
            self.screen.blit(self.loading_text, (0, 0))
            return State(GameState.FLIP)
        return None

    def on_init(self):
        pass
