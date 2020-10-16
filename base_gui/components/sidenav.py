from typing import Callable, Any, List

import pygame

from base_gui.app_logging import log_child
from base_gui.components.callbackbutton import CallbackButton
from pygame_widgets import Button

DEFAULT_OFFSET_X = 0
DEFAULT_OFFSET_Y = 40


class SideNav(object):
    buttons: List[CallbackButton] = []

    def __init__(self,
                 screen,
                 nav_rect_bounds,
                 offset_x=DEFAULT_OFFSET_X,
                 offset_y=DEFAULT_OFFSET_Y,
                 callback: Callable[[Button], Any] = None
                 ):
        assert screen is not None
        assert nav_rect_bounds is not None
        self.screen = screen
        self.nav_rect_bounds = nav_rect_bounds
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.callback = callback

    def render_nav_backlight(self, width=200):
        s = pygame.Surface((width, self.screen.get_size()[1]))  # the size of your rect
        s.set_alpha(255)  # alpha level
        s.fill((200, 200, 200))  # this fills the entire surface
        self.screen.blit(s, (0, 0))  # (0,0) are the top-left coordinates

    def add_button(self, label):
        button = Button(
            self.screen,
            self.nav_rect_bounds.left + 5 + len(self.buttons) * self.offset_x,
            self.nav_rect_bounds.top + 10 + len(self.buttons) * self.offset_y,
            self.nav_rect_bounds.width - 10,
            30,
            shadowDistance=150,
            text=label,
            fontSize=14,
            margin=10,
            inactiveColour=(230, 230, 230),
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
