import logging
from typing import Callable, Any

import pygame
from pygame import Vector2, RESIZABLE, DOUBLEBUF

from base_gui.constants import SIM_SIZE, NAV_WIDTH
from base_gui.gui_components.sidenav import SideNav
from base_gui.utils.reference_frame import vector2_to_int_tuple


class Game(object):
    def __init__(self, size: Vector2):
        self.screen = None
        self.window = None
        self.size = size

        self.nav_rect_bounds = pygame.Rect(0, 0, NAV_WIDTH, SIM_SIZE.y)
        self.side_menu = None

    def create_game(self):
        pygame.init()
        self.window = pygame.display.set_mode(vector2_to_int_tuple(self.size), DOUBLEBUF | RESIZABLE)
        self.screen = pygame.display.get_surface()
        pygame.display.flip()

    def add_nav_menu(self, generic_callback=None):
        self.side_menu = SideNav(self.screen, self.nav_rect_bounds, generic_callback=generic_callback)

    def add_nav_button(self, label: str, button_callback: Callable[[Any], Any] = None):
        if self.side_menu is None:
            logging.ERROR("Should run add_nav_menu before adding buttons.")
        self.side_menu.add_button(label=label, button_callback=button_callback)

