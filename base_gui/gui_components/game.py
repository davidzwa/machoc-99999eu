import logging
from abc import abstractmethod, ABC
from typing import Callable, Any

import pygame
from pygame import Vector2, RESIZABLE, DOUBLEBUF, Surface

from base_gui.constants import SIM_SIZE, NAV_WIDTH
from base_gui.gui_components.sidenav import SideNav
from base_gui.gui_components.timeline import Timeline
from base_gui.utils.reference_frame import vector2_to_int_tuple


class Game(ABC):
    def __init__(self, size: Vector2):
        self.screen: Surface = None
        self.size = size

        self.nav_rect_bounds = pygame.Rect(0, 0, NAV_WIDTH, SIM_SIZE.y)
        self.side_menu = None
        self.timeline = None

    def create_game(self, generic_nav_callback=None):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 15)
        self.screen = pygame.display.set_mode(vector2_to_int_tuple(self.size), DOUBLEBUF | RESIZABLE)
        self.side_menu = SideNav(self.screen, self.nav_rect_bounds, generic_callback=generic_nav_callback)
        pygame.display.set_caption("Six Figure Potential - MacRouting Simulator")
        pygame.display.flip()

    def add_nav_button(self, label: str, button_callback: Callable[[Any], Any] = None):
        if self.side_menu is None:
            logging.ERROR("Should run add_nav_menu before adding buttons.")
        return self.side_menu.add_button(label=label, button_callback=button_callback)

    def __assert_checkbox(self, group_index, index):
        assert self.side_menu.checkbox_groups is not None
        assert self.side_menu.checkbox_groups[group_index] is not None
        assert self.side_menu.checkbox_groups[group_index].rows > index

    def reset_checkbox(self, group_index, index, state=False):
        self.__assert_checkbox(group_index, index)
        self.side_menu.checkbox_groups[group_index].selected[index] = state

    def get_checkbox_value(self, group_index, index):
        self.__assert_checkbox(group_index, index)
        return self.side_menu.checkbox_groups[group_index].selected[index]

    @abstractmethod
    def add_nav_checkboxgroup_specific(self, sim_labels: tuple):
        """
        Enforce the inheritee to implement this, increasing understanding of the menu build-up
        """
        pass
        # Example
        # self.side_menu.clear_checkbox_groups()
        # self.add_nav_checkboxgroup_generic(MENU_CHECKBOXES_GENERIC)
        # self.add_nav_checkboxgroup_generic(sim_labels)

    def add_nav_checkboxgroup_generic(self, labels: tuple):
        assert len(labels) > 0
        if self.side_menu is None:
            logging.ERROR("Should run add_nav_menu before adding buttons.")
        return self.side_menu.add_checkbox_group(labels)

    def add_timeline(self, position: Vector2, size: Vector2):
        self.timeline = Timeline(self.screen, position, size, lambda: self.timeline_select_update())

    def timeline_select_update(self):
        print("Timeline updated")
