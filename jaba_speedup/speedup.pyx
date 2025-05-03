# distutils: language=c++
# cython: profile=True
from copy import copy
from settings import DEBUG
import traceback
import sys
from typing import Optional, Tuple
import time


def copy_matrix(list matrix) -> list:
    copy_matrix = []
    for i in range(len(matrix)):
        copy_matrix.append([])
        for j in range(len(matrix[i])):
            copy_matrix[i].append([])
            for obj in matrix[i][j]:
                copy_obj = copy(obj)
                copy_matrix[i][j].append(copy_obj)
    return copy_matrix

cpdef int map_value(double x, double in_min, double in_max, double out_min, double out_max):
    return round((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


class SmoothMove:
    """
    A class for smooth object movement and separating maths from rendering
    """

    def __init__(self, start_x_pixel: int, start_y_pixel: int, x_pixel_delta: int, y_pixel_delta: int,
                 duration_seconds: float, start_time: Optional[float] = None):
        if x_pixel_delta == y_pixel_delta and y_pixel_delta == duration_seconds and duration_seconds == 0:
            if DEBUG:
                print("ERROR: Possible division by zero!!!!", file=sys.stderr)
                traceback.print_stack()
        self.start_x_pixel: int = start_x_pixel
        self.start_y_pixel: int = start_y_pixel
        self.x_pixel_delta: int = x_pixel_delta
        self.y_pixel_delta: int = y_pixel_delta
        self._duration_seconds: float = duration_seconds
        if start_time is None:
            start_time = time.time()
        self._start_time: float = start_time

    def rerun(self, duration_seconds: float):
        self._start_time = time.time()
        self._duration_seconds = duration_seconds

    @property
    def elapsed_seconds(self) -> float:
        return min(time.time() - self._start_time, self._duration_seconds)

    @property
    def done(self) -> bool:
        return self.elapsed_seconds >= self._duration_seconds

    def update_x_and_y(self) -> Tuple[int, int]:
        """
        Update x and y of the object.

        :returns: Tuple with new x and y
        """
        elapsed_time = self.elapsed_seconds
        new_x = map_value(elapsed_time,
                          0, self._duration_seconds,
                          self.start_x_pixel, self.start_x_pixel + self.x_pixel_delta)
        new_y = map_value(elapsed_time,
                          0, self._duration_seconds,
                          self.start_y_pixel, self.start_y_pixel + self.y_pixel_delta)
        return new_x, new_y
