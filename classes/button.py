import pygame
import os, os.path

from classes.SpriteManager import SpriteManager

class Button:
    def __init__(self, x, y, width, height, outline, settings, text="", action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.settings = settings
        self.action = action
        self.outline = outline
        pygame.font.init() # Чтобы не инициализировать шрифт каждый раз
        self.font = pygame.font.SysFont('segoeuisemibold', self.settings.text_size)

    def draw(self, screen):
        if self.outline:
            pygame.draw.rect(screen, self.outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        color = self.settings.button_color if not self.is_over(
            pygame.mouse.get_pos()) else self.settings.button_color_hover
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0)

        if self.text != "":
            lines = self.text.split('\n')
            text_height = 0
            for index, line in enumerate(lines):
                line = self.font.render(line, True, (255, 255, 255))
                text_height += line.get_height()
                screen.blit(
                    line,
                    (
                        self.x + (self.width / 2 - line.get_width() / 2),
                        self.y + (self.height / 2 + (text_height / len(lines) *
                                                     (len(lines) // 2 * -1 + index))) -
                        (line.get_height() / 2 if len(lines) == 1 else 0)
                    )
                )

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and self.is_over(pygame.mouse.get_pos()) \
                    and self.action:
                self.action()
                return True
        return False

    def is_over(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False

class Object_Button(Button):
    def __init__(self, x, y, width, height, outline, settings, text="", action=None):
        super().__init__(x, y, width, height, outline, settings, text, action)
        DIR = f'./sprites/{self.text}'
        self.sprite_count = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        self.state_count = self.sprite_count // 3