import pygame


def draw_rounded_rect(surface, color, rect, border_radius):
    ''' Draw a rectangle with rounded corners.
    Would prefer this:
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)
    but this option is not yet supported in my version of pygame so do it ourselves.

    We use anti-aliased circles to make the corners smoother
    '''
    if rect.width < 2 * border_radius or rect.height < 2 * border_radius:
        raise ValueError(
            f"Both height (rect.height) and width (rect.width) must be > 2 * corner radius ({border_radius})")

    # need to use anti aliasing circle drawing routines to smooth the corners
    pygame.gfxdraw.aacircle(surface, rect.left + border_radius, rect.top + border_radius, border_radius, color)
    pygame.gfxdraw.aacircle(surface, rect.right - border_radius - 1, rect.top + border_radius, border_radius, color)
    pygame.gfxdraw.aacircle(surface, rect.left + border_radius, rect.bottom - border_radius - 1, border_radius, color)
    pygame.gfxdraw.aacircle(surface, rect.right - border_radius - 1, rect.bottom - border_radius - 1, border_radius,
                            color)

    pygame.gfxdraw.filled_circle(surface, rect.left + border_radius, rect.top + border_radius, border_radius, color)
    pygame.gfxdraw.filled_circle(surface, rect.right - border_radius - 1, rect.top + border_radius, border_radius,
                                 color)
    pygame.gfxdraw.filled_circle(surface, rect.left + border_radius, rect.bottom - border_radius - 1, border_radius,
                                 color)
    pygame.gfxdraw.filled_circle(surface, rect.right - border_radius - 1, rect.bottom - border_radius - 1,
                                 border_radius, color)

    rect_tmp = pygame.Rect(rect)

    rect_tmp.width -= 2 * border_radius
    rect_tmp.center = rect.center
    pygame.draw.rect(surface, color, rect_tmp)

    rect_tmp.width = rect.width
    rect_tmp.height -= 2 * border_radius
    rect_tmp.center = rect.center
    pygame.draw.rect(surface, color, rect_tmp)


def draw_bordered_rounded_rect(surface, color, rect, border_color, corner_radius, border_thickness):
    if corner_radius < 0:
        raise ValueError(f"border radius ({corner_radius}) must be >= 0")

    rect_tmp = pygame.Rect(rect)
    center = rect_tmp.center

    if border_thickness:
        if corner_radius <= 0:
            pygame.draw.rect(surface, border_color, rect_tmp)
        else:
            draw_rounded_rect(surface, rect_tmp, border_color, corner_radius)

        rect_tmp.inflate_ip(-2 * border_thickness, -2 * border_thickness)
        inner_radius = corner_radius - border_thickness + 1
    else:
        inner_radius = corner_radius

    if inner_radius <= 0:
        pygame.draw.rect(surface, color, rect_tmp)
    else:
        draw_rounded_rect(surface, rect_tmp, color, inner_radius)
