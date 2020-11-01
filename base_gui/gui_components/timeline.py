from typing import Callable, Any

from pygame import Vector2
from pygame.surface import Surface

from base_gui.constants import SimConsts
from pygame_widgets import Slider


class Timeline(object):

    def __init__(self,
                 screen: Surface,
                 position: Vector2,
                 size: Vector2,
                 updatetime_callback: Callable[[Any], Any]
                 ):
        self.screen = screen
        self.position = position
        self.size = size

        assert updatetime_callback is not None
        self.update_callback = updatetime_callback

        self.nodes_slider = Slider(
            self.screen, int(self.position.x), int(self.position.y), int(self.size.x), int(self.size.y),
            min=2, max=10, step=1, initial=10)
        self.time_slider = Slider(
            self.screen, int(self.position.x), int(self.position.y)+50, int(self.size.x), int(self.size.y),
            min=0, max=SimConsts.TIME_MAX_STEPS-1, step=SimConsts.TIME_STEP, initial=0)

    def render(self):
        self.nodes_slider.draw()
        self.time_slider.draw()
