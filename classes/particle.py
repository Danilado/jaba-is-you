"""Particle class module"""
import os
from math import sin, cos
from random import randint, uniform
from typing import Optional, Tuple, Union

import pygame

from elements.global_classes import sprite_manager
from global_types import COLOR
from settings import DEBUG, FPS

FADE_OUT_DURATION = int(FPS/3)


class ParticleStrategy:
    """Particle motion strategy class"""

    def __init__(self, x_dimensions: Optional[Tuple[int, int]] = None, y_dimensions: Optional[Tuple[int, int]] = None,
                 size: Optional[Tuple[int, int]] = None, rotation: Optional[Tuple[int, int]] = None, wobble: int = 0,
                 duration: Optional[float] = None, loop: bool = False, randomize_start_values: bool = False):
        """Initialisation of the particle strategy

        :param x_dimensions: x-coordinates of the beginning and end of the particle motion, defaults to None
        :type x_dimensions: Tuple[int, int], optional
        :param y_dimensions: y-coordinates of the beginning and end of the particle motion, defaults to None
        :type y_dimensions: Tuple[int, int], optional
        :param size: Particle size, defaults to None
        :type size: Tuple[int, int], optional
        :param rotation: rotation angle of the particle sprite at the beginning and end of the motion, defaults to None
        :type rotation: Tuple[int, int], optional
        :param wobble: particle displacement in pixels during motion, defaults to 0
        :type wobble: int, optional
        :param duration: Animation length in seconds, defaults to None
        :type duration: int, optional
        :param loop: is animation looped, defaults to False
        :type loop: bool, optional
        :param randomize_start_values: Should initial values be randomised within the entered values, defaults to False
        :type randomize_start_values: bool, optional
        """
        try:
            self.duration = duration * 1000
            self.loop = loop
            self.wobble = wobble

            self.x_position = x_dimensions[0]
            self.x_start = x_dimensions[0]
            self.x_offset = x_dimensions[1] - self.x_start

            self.y_position = y_dimensions[0]
            self.y_start = y_dimensions[0]
            self.y_offset = y_dimensions[1] - self.y_start

            self.size = size[0]
            self.size_start = size[0]
            self.size_offset = size[1] - self.size_start

            self.angle = rotation[0]
            self.angle_start = rotation[0]
            self.angle_offset = rotation[1] - self.angle_start

            self.time_randomizer = 0

            self.fade_out_frames = 0
            self.opacity = 1

            if randomize_start_values:
                self.x_position = randint(min(x_dimensions[0], x_dimensions[1]), max(
                    x_dimensions[0], x_dimensions[1]))
                self.y_position = randint(min(y_dimensions[0], y_dimensions[1]), max(
                    y_dimensions[0], y_dimensions[1]))
                self.angle = randint(
                    min(rotation[0], rotation[1]), max(rotation[0], rotation[1]))
                self.time_randomizer = uniform(0, self.duration)

            self.start_timestamp = pygame.time.get_ticks()
        except IndexError:
            if DEBUG:
                print("IndexError in particles, for fuck's sake. Something's not right")
                print(x_dimensions, y_dimensions, rotation, duration, loop)
                print('^ Incorrect arguments are passed in the initialisation of the particle strategy ^')
        except TypeError:
            if DEBUG:
                print("TypeError in particles, for fuck's sake. Something's not right")
                print(x_dimensions, y_dimensions, rotation, duration, loop)
                print('^ Incorrect arguments are passed in the initialisation of the particle strategy ^')

    def update_values(self):
        timestamp = pygame.time.get_ticks()
        time_position = timestamp + self.time_randomizer - self.start_timestamp
        if time_position > self.duration:
            if self.loop:
                self.start_timestamp = timestamp + self.time_randomizer
                self.x_position = self.x_start
                self.y_position = self.y_start
                self.angle = self.angle_start
                self.size = self.size_start
                return self.update_values()
            elif self.fade_out_frames < FADE_OUT_DURATION:
                self.fade_out_frames += 1
                self.opacity = 1 - self.fade_out_frames/FADE_OUT_DURATION
                self.size = self.size_start / FADE_OUT_DURATION * \
                    (FADE_OUT_DURATION - self.fade_out_frames)
            else:
                return False

        time_offset = time_position / self.duration

        self.x_position = self.x_start + self.x_offset * time_offset
        self.y_position = self.y_start + self.y_offset * time_offset

        if self.wobble:
            self.x_position += self.wobble * \
                cos((timestamp+self.time_randomizer)/1000)
            self.y_position += self.wobble * \
                sin((timestamp+self.time_randomizer)/1000)

        if time_position < self.duration:
            self.size = self.size_start + self.size_offset * time_offset

        self.angle = self.angle_start + self.angle_offset * time_offset

        return True


class Particle:
    def __init__(self, name: str,
                 strategy: Union[ParticleStrategy, str] = None, color: COLOR = 'white'):
        self._sprite_name: str = name
        self.color = color

        self.strategy = strategy

        self._sprites = self._get_sprites()
        self.sprite_index = 0
        self.animation_timestamp = pygame.time.get_ticks()

    def _get_sprites(self):
        path = os.path.join('./', 'sprites', self._sprite_name)
        states = [sprite_manager.get(os.path.join(
            path, name), color=self.color) for name in os.listdir(path)]
        return states

    @property
    def sprite_name(self):
        return self._sprite_name

    @sprite_name.setter
    def sprite_name(self, value: str):
        self._sprite_name = value
        self._sprites = self._get_sprites()

    def update(self):
        if self.strategy.update_values():
            if pygame.time.get_ticks() - self.animation_timestamp >= 200:
                self.sprite_index += 1
                self.sprite_index %= len(self._sprites)
                self.animation_timestamp = pygame.time.get_ticks()
            return True
        return False

    def draw(self, screen):
        if self.update():
            cur_sprite = pygame.transform.scale(
                pygame.transform.rotate(
                    self._sprites[self.sprite_index], int(self.strategy.angle)),
                (self.strategy.size, )*2)
            cur_sprite.set_alpha(self.strategy.opacity*255)
            screen.blit(
                cur_sprite,
                (self.strategy.x_position, self.strategy.y_position))
            return True
        return False
