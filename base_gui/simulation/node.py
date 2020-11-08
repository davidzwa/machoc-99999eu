from typing import List

import pygame
from pygame import Vector2, Surface, gfxdraw
from pygame.rect import Rect

from base_gui.constants import SimConsts
from base_gui.mac.actorstate import MacState
from base_gui.simulation.wave import Wave
from base_gui.utils.reference_frame import vector2_global_to_local, scale_tuple_pix2meter


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

        self.waves: List[Wave] = list()
        self.update_global_position()

    def update_global_position(self):
        # Function for updating position (allow GUI/simulation rescaling)
        self.global_position = vector2_global_to_local(
            self.position_meters,
            self.reference_frame,
            self.local_origin_offset,
            True)

    def set_color_by_state(self, state: MacState):
        self.color = SimConsts.STATE_COLOR_DICT[state]

    def set_wavefronts(self, wave_specs: List[Vector2], message_types):
        """
        Visualize multiple in-transit message wavefronts.
        Each Vector2 contains 2 distances: min,max wave-distance to shape the donut
        """

        # Iterate wave_specs
        self.waves = list()
        for index, minmax_donut in enumerate(wave_specs):
            assert minmax_donut[1] >= 0
            if minmax_donut == 0:
                continue
            minmax_donut = scale_tuple_pix2meter(minmax_donut, reverse=True)
            if minmax_donut[0] > 0:
                self.add_wavefront(minmax_donut[0], minmax_donut[1], message_types[index])
            else:
                self.add_wavefront(0, minmax_donut[1], message_types[index])

    def add_wavefront(self, min_radius, max_radius, message_type):
        color = SimConsts.MESSAGE_COLOR_DICT[message_type]

        self.waves.append(
            Wave(self.screen,
                 min_radius, max_radius, SimConsts.WAVES_DENSITY, color,
                 global_position=self.global_position)
        )

    def render(self, disable_node_title=False):
        if disable_node_title is False:
            self.font_surface = self.font.render(self.node_title, True, pygame.Color("black"))
            self.screen.blit(self.font_surface, dest=(self.global_position[0] + 5, self.global_position[1] - 10))
        pygame.gfxdraw.aacircle(self.screen,
                                int(self.global_position[0]), int(self.global_position[1]),
                                self.__radius,
                                self.color)
        pygame.gfxdraw.filled_circle(self.screen,
                                     int(self.global_position[0]),
                                     int(self.global_position[1]),
                                     self.__radius,
                                     self.color)

    def render_waves(self):
        assert self.waves is not None
        for wave in self.waves:
            wave.render()
