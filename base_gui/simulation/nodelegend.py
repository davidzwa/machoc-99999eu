import pygame
from pygame import Vector2, Surface, gfxdraw

from base_gui.constants import SimConsts
from base_gui.mac.actorstate import MacState


class NodeLegend(object):
    """
    A class representing both a MAC node with label
    This is meant for a legend only
    """

    def __init__(self,
                 global_position: Vector2,
                 screen: Surface,
                 labeled_state: MacState,
                 label: str = ""):
        self.screen = screen
        self.__radius = 3
        self.set_color_by_state(labeled_state)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)
        self.label = label
        self.global_position = global_position

    def set_color_by_state(self, state: MacState):
        self.color = SimConsts.STATE_COLOR_DICT[state]

    def render(self):
        self.font_surface = self.font.render(self.label, True, pygame.Color("black"))
        self.screen.blit(self.font_surface, dest=(self.global_position[0] + 5, self.global_position[1] - 4))
        pygame.gfxdraw.aacircle(self.screen,
                                int(self.global_position[0]), int(self.global_position[1]),
                                self.__radius,
                                self.color)
        pygame.gfxdraw.filled_circle(self.screen,
                                     int(self.global_position[0]),
                                     int(self.global_position[1]),
                                     self.__radius,
                                     self.color)
