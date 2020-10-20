import pygame
from pygame import Vector2, Surface, gfxdraw
from pygame.rect import Rect

from base_gui.utils.reference_frame import vector2_global_to_local


class Node(object):
    """
    A class representing both a ROUTING/MAC node in [x,y] unit meters
    Uses conversion transform in utils to render to pixels
    """

    def __init__(self,
                 position_meters: Vector2,
                 reference_frame: Rect,
                 local_origin: Vector2,
                 screen: Surface,
                 color: pygame.Color,
                 node_title: str = ""):
        self.position_meters = position_meters
        self.screen = screen
        self.reference_frame = reference_frame
        self.local_origin_offset = local_origin
        self.__radius = 3
        self.color = color

        self.font = pygame.font.Font(pygame.font.get_default_font(), 11)
        self.node_title = node_title

    def render(self, disable_node_title=False):
        global_vector = vector2_global_to_local(
            self.position_meters,
            self.reference_frame,
            self.local_origin_offset,
            True)
        if disable_node_title is False:
            self.font_surface = self.font.render(self.node_title, True, pygame.Color("black"))
            self.screen.blit(self.font_surface, dest=(global_vector.x + 5, global_vector.y - 10))
        pygame.gfxdraw.aacircle(self.screen,
                                int(global_vector.x), int(global_vector.y),
                                self.__radius,
                                self.color)
        pygame.gfxdraw.filled_circle(self.screen,
                                     int(global_vector.x),
                                     int(global_vector.y),
                                     self.__radius,
                                     self.color)
