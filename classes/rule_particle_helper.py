import time
from random import choice
from typing import Optional, TYPE_CHECKING, Sequence, Set, List, Callable

from classes.objects import Object
from classes.particle import Particle, ParticleStrategy
from classes.text_rule import TextRule
from elements.global_classes import sprite_manager
from global_types import COLOR

if TYPE_CHECKING:
    from elements.play_level import PlayLevel


class ParticleMover:
    """
    The class that moves partials
    """

    def __init__(self, x_offset: Sequence[int], y_offset: Sequence[int], size: Sequence[int],
                 max_rotation: Sequence[int], wait_delay: float, duration: float, particle_sprite_name: str,
                 count: Optional[Sequence[int]] = None, sprite_colors: Optional[Sequence[COLOR]] = None):
        """
        Class constructor

        :param x_offset:
            Range of numbers in which the indentation for the particle on the x-axis will be randomly selected
        :param y_offset:
            Range of numbers in which the indentation for the particle on the x-axis will be randomly selected
        :param size: The range of numbers in which the size for the particle will be randomly selected
        :param max_rotation:
            The range of numbers in which the degree of rotation for the particle will be randomly selected
        :param wait_delay: Number representing the delay between particle creation, negative if always called manually
        :param duration: Particle duration
        :param count: Range of numbers in which the number of particles at a time will be randomly selected
        :param particle_sprite_name: The name of the particle sprite
        """
        # Particle settings
        self.count = count if count is not None else range(1, 4)
        self.wait_delay: float = wait_delay
        self.duration: float = duration
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.size = size
        self.max_rotation = max_rotation
        self.particle_sprite_name = particle_sprite_name
        self.sprite_colors: Optional[Sequence[COLOR]] = sprite_colors
        # Horrible background
        self._level_processor: Optional["PlayLevel"] = None
        self._rule_objects: Set[Object] = set()
        self._timer: Optional[float] = None

    def for_rule_objects(self, func: Callable):
        for rule in self._rule_objects:
            func(rule)

    def update_on_apply(self, level_processor: "PlayLevel", rule_object: Object, color: Optional[str] = None,
                        force_not_start: bool = False):
        """
        Encapsulation :attr:`~.ParticleMover.rule_object` and :attr:`~.ParticleMover.level_processor`
        That is, sets them.

        :param force_not_start:
            Workaround. If True, it does not cause the :meth:`~.ParticleMover.start`.
            Only set True if you realise what you are doing.
        :param level_processor: Level handler
        :param rule_object: Object to which particles are applied
        :param color: Object from which the colour is to be taken
        :return: Nothing
        """
        if level_processor != self._level_processor:
            self._rule_objects.clear()
        self._level_processor = level_processor
        have_rule_object = False
        for rule in self._rule_objects:
            if repr(rule) == repr(rule_object):
                have_rule_object = True
                break
        if not have_rule_object:
            self._rule_objects.clear()
            self._rule_objects.add(rule_object)
        if color is not None:
            palette_pixel_position = sprite_manager.default_colors[color]
            self.sprite_colors = [self._level_processor.current_palette.pixels[
                palette_pixel_position[1]][palette_pixel_position[0]]]
        if not self.started and not force_not_start:
            self.start()

    def update_on_rules_changed(self, new_rules: List[TextRule], rule_name: str):
        need_to_stop = True
        for rule in new_rules:
            rule_end = f' is {rule_name}'
            if rule_end in rule.text_rule and rule.text_rule[:rule.text_rule.index(rule_end)] in \
                    [i.name for i in self._rule_objects]:
                need_to_stop = False
        if self.started and need_to_stop:
            self.stop()
            return False
        return True

    def stop(self):
        """
        Sends a request to stop the particle change

        :return: Nothing
        """
        if not self.started:
            return
        self._timer = None
        self._rule_objects.clear()

    def start(self):
        """
        Starts the particle change

        :return: Nothing
        """
        if self.started:
            return
        self._timer = time.time()

    @property
    def started(self) -> bool:
        """
        .. getter: Returns a bool indicating whether the thread is running or not

        .. setter:
            Nope.
            Use :meth:`~.ParticleMover.start` to start
            or :meth:`~.ParticleMover.stop` to stop
        """
        return self._timer is not None

    @property
    def rule_objects(self) -> Set[Object]:
        return self._rule_objects

    def _work_one_particle(self, rule_object: Object):
        if self._level_processor is None:
            raise RuntimeError("self._level_processor is not initialized")
        for _ in range(choice(self.count)):
            x_offset = choice(self.x_offset)
            y_offset = choice(self.y_offset)
            size = choice(self.size)
            max_rotation = choice(self.max_rotation)
            color: COLOR
            if self.sprite_colors is None:
                palette_pixel_position = sprite_manager.default_colors[rule_object.name]
                color = self._level_processor.current_palette.pixels[
                    palette_pixel_position[1]][
                    palette_pixel_position[0]]
            else:
                color = choice(self.sprite_colors)
            self._level_processor.particles.append(Particle(self.particle_sprite_name, ParticleStrategy(
                (rule_object.xpx, rule_object.xpx + x_offset),
                (rule_object.ypx, rule_object.ypx + y_offset),
                (size, size),
                (0, max_rotation), 10,
                self.duration,
                randomize_start_values=True
            ), color))

    def every_frame(self, force_draw: bool = False):
        """There used to be a thread here, but now there's this function here"""
        if not force_draw and (self._timer is None or self.wait_delay < 0 or (time.time() - self._timer) < self.wait_delay):
            return
        for rule_object in self._rule_objects:
            self._work_one_particle(rule_object)
        self._timer = time.time()
