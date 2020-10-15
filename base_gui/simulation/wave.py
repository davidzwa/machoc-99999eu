import pygame
from pygame import gfxdraw, SRCALPHA, BLEND_ADD

TARGET_SIZE = 50  # Ellipse x/y radii
BG_ALPHA_COLOR = (0, 0, 255)


class Wave(object):
    def __init__(self, screen, bounds_rect):
        assert screen is not None
        self.screen = screen
        self.rect = bounds_rect

    def render(self, x, y):
        self.width = 5
        self.filled = False
        self.color = (120, 120, 120)
        self.DrawTarget()
        # gfxdraw.aacircle(self.screen, x, y, 20, (0, 0, 255))
        # gfxdraw.filled_circle(self.screen, 150, 50, 15, (0, 0, 255))
        # pygame.draw.circle(self.screen, (0, 0, 255), (150, 50), 15, 1)

    def DrawTarget(self):
        # outside antialiased circle
        pygame.gfxdraw.aacircle(self.screen,
                                self.rect.left + int(self.rect.width / 2),
                                self.rect.top + int(self.rect.height / 2),
                                int(self.rect.width / 2 - 1),
                                self.color)

        # outside filled circle
        pygame.gfxdraw.filled_ellipse(self.screen,
                                      self.rect.left + int(self.rect.width / 2),
                                      self.rect.top + int(self.rect.height / 2),
                                      int(self.rect.width / 2 - 1),
                                      int(self.rect.width / 2 - 1),
                                      self.color)

        temp = pygame.Surface((TARGET_SIZE, TARGET_SIZE), SRCALPHA)  # the SRCALPHA flag denotes pixel-level alpha

        if (self.filled == False):
            # inside background color circle

            pygame.gfxdraw.filled_ellipse(temp,
                                          self.rect.left + int(self.rect.width / 2),
                                          self.rect.top + int(self.rect.height / 2),
                                          int(self.rect.width / 2 - self.width),
                                          int(self.rect.width / 2 - self.width),
                                          BG_ALPHA_COLOR)

            # inside antialiased circle
            pygame.gfxdraw.aacircle(temp,
                                    self.rect.left + int(self.rect.width / 2),
                                    self.rect.top + int(self.rect.height / 2),
                                    int(self.rect.width / 2 - self.width),
                                    BG_ALPHA_COLOR)

        self.screen.blit(temp, (0, 0), None, BLEND_ADD)
