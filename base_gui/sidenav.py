from typing import Callable, Any, List

from base_gui.app_logging import log_child
from base_gui.callbackbutton import CallbackButton
from pygame_widgets import Button

DEFAULT_OFFSET_X = 0
DEFAULT_OFFSET_Y = 40


class SideNav(object):
    buttons: List[CallbackButton] = []

    def __init__(self,
                 screen,
                 button_rect,
                 offset_x=DEFAULT_OFFSET_X,
                 offset_y=DEFAULT_OFFSET_Y,
                 callback: Callable[[Button], Any] = None
                 ):
        assert screen is not None
        assert button_rect is not None
        self.screen = screen
        self.button_rect = button_rect
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.callback = callback

    def add_button(self, label):
        button = Button(
            self.screen,
            self.button_rect.left + len(self.buttons) * self.offset_x,
            self.button_rect.top + len(self.buttons) * self.offset_y,
            self.button_rect.width,
            self.button_rect.height,
            shadowDistance=150,
            text=label,
            fontSize=14,
            margin=10,
            inactiveColour=(240, 240, 240),
            pressedColour=(255, 255, 240),
            radius=5
        )
        cbutton = CallbackButton(button, self.button_clicked)
        self.buttons.append(cbutton)
        return button

    def button_clicked(self, cbutton: CallbackButton):
        log_child('button clicked:', cbutton.button.text)

        self.callout(cbutton)

    def callout(self, cbutton: CallbackButton):
        if self.callback is not None:
            self.callback(cbutton.state)

    def render(self, events: Any):
        for cbutton in self.buttons:
            cbutton.draw_inner()
            cbutton.button.listen(events)
