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
                 bounds_rect: Rect,
                 local_origin_offset: Vector2,
                 radius_max,
                 radius_step):
        assert screen is not None
        self.screen = screen
        self.rect = bounds_rect
        self.local_origin_offset = local_origin_offset
        self.origin = (0, 0)  # 2D tuple within rect, we dont validate: expect the user is careful
        self.radius_max_meters = radius_max  # meters/size units
        self.radius_step_pixels = radius_step  # pixels

    def adjust_origin_local(self, coords_local_meters):
        self.origin = (coords_local_meters[0], coords_local_meters[1])

    def render(self):
        self.width = 5
        self.filled = False
        self.color = np.array([120, 120, 120])
        for i in range(50, self.radius_max_meters * self.radius_step_pixels, self.radius_step_pixels):
            self.draw_wave_circle(i)

    def draw_wave_circle(self, radius):
        # https://abarry.org/antialiased-rings-filled-circles-in-pygame/
        # outside antialiased circle
        pixel_origin = translate_global_to_local(
            scale_tuple_pix2meter(self.origin, reverse=True),
            self.rect,
            self.local_origin_offset,
            reverse=True)
        pygame.gfxdraw.aacircle(self.screen,
                                pixel_origin[0],
                                pixel_origin[1],
                                radius,
                                self.color)
        temp = pygame.Surface((TARGET_SIZE, TARGET_SIZE), SRCALPHA)  # the SRCALPHA flag denotes pixel-level alpha
        self.screen.blit(temp, (0, 0), None, BLEND_ADD)

    def translate_to_global_x(self):
        return self.origin[0] + self.rect.left

    def translate_to_global_y(self):
        return self.origin[1] + self.rect.top
