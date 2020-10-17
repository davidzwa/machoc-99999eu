import pygame
from pygame import Vector2, Surface, gfxdraw
from pygame.rect import Rect

from base_gui.utils.reference_frame import vector2_global_to_local, vector2_to_int_tuple


class Node(object):
    """
    A class representing both a ROUTING/MAC node in [x,y] unit meters
    Uses conversion transform in utils to render to pixels
    """

    def __init__(self, position_meters: Vector2, reference_frame: Rect, screen: Surface, color: pygame.Color):
        self.position_meters = position_meters
        self.screen = screen
        self.reference_frame = reference_frame
        self.__radius = 3
        self.color = color

    def render(self):
        global_vector = vector2_global_to_local(self.position_meters, self.reference_frame, True)
        # global_tuple = vector2_to_int_tuple(global_vector)
        pygame.gfxdraw.aacircle(self.screen, int(global_vector.x), int(global_vector.y), self.__radius, self.color)
        pygame.gfxdraw.filled_circle(self.screen,
                                     int(global_vector.x),
                                     int(global_vector.y),
                                     self.__radius,
                                     self.color)
        # self.screen.
