import numpy as np
import pygame
from pygame import gfxdraw, SRCALPHA, BLEND_ADD, Surface, Vector2
from pygame.rect import Rect

from base_gui.utils.reference_frame import scale_tuple_pix2meter, translate_global_to_local

TARGET_SIZE = 50  # Ellipse x/y radii
BG_ALPHA_COLOR = (122, 122, 255)


class Wave(object):
    def __init__(self,
                 screen: Surface,
                 radius_min,
                 radius_max,
                 radius_steps,
                 color,
                 global_position: Vector2):
        assert screen is not None
        self.screen = screen
        self.global_position = global_position
        self.radius_min_pixels = int(radius_min)
        self.radius_max_pixels = int(radius_max)  # meters/size units
        self.radius_steps = radius_steps  # pixels
        self.color = color

    def render(self):
        self.width = 5
        self.filled = False
       # self.color = np.array([120, 120, 120])
        if self.radius_steps > 0:
            for i in range(self.radius_min_pixels, self.radius_max_pixels, self.radius_steps):
                self.draw_wave_circle(i)
        else:
            self.draw_wave_circle(self.radius_max_pixels)

    def draw_wave_circle(self, radius):
        # https://abarry.org/antialiased-rings-filled-circles-in-pygame/
        # outside antialiased circle
        pygame.gfxdraw.aacircle(self.screen,
                                self.global_position[0],
                                self.global_position[1],
                                radius,
                                self.color)
        temp = pygame.Surface((TARGET_SIZE, TARGET_SIZE), SRCALPHA)  # the SRCALPHA flag denotes pixel-level alpha
        self.screen.blit(temp, (0, 0), None, BLEND_ADD)
