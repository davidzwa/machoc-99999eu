from typing import Callable, Any

from pygame_widgets import Button


class CallbackButton(object):
    state = dict()
    def __init__(self, button: Button, callback: Callable[[Any], Any] = None):
        self.callback = callback
        assert button is not None
        self.button = button

        if self.callback is not None:
            button.onClick = lambda: callback(self)

    def draw_inner(self):
        self.button.draw()