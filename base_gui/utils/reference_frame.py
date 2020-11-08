from pygame import Vector2
from pygame.rect import Rect

from base_gui.constants import get_pixel_meter_ratio


def scale_pixels_to_meters(value, reverse=False):
    # This function serves as reference frame scaling (pixels/meter)
    if not reverse:
        return value / get_pixel_meter_ratio()
    else:
        return int(value * get_pixel_meter_ratio())


def scale_tuple_pix2meter(coord, reverse=False):
    return (
        scale_pixels_to_meters(coord[0], reverse),
        scale_pixels_to_meters(coord[1], reverse),
    )


def translate_global_to_local(position: tuple, reference_frame_rect: Rect, local_origin: Vector2, reverse=False):
    # This function serves as reference frame translation
    if not reverse:
        return (position[0] - int(local_origin.x) - reference_frame_rect.left,
                position[1] - int(local_origin.y) - reference_frame_rect.top)
    else:
        return (int(position[0] + local_origin.x + reference_frame_rect.left),
                int(position[1] + local_origin.y + reference_frame_rect.top))


def vector2_global_to_local(vector: Vector2, reference_frame_rect, local_origin_offset, reverse: bool = False):
    if not reverse:
        pos = (vector.x, vector.y)
        pos_transformed_local = scale_tuple_pix2meter(
            translate_global_to_local(pos, reference_frame_rect, local_origin_offset))
        return Vector2(pos_transformed_local)
    else:
        pos = (vector.x, vector.y)
        pos_scaled = scale_tuple_pix2meter(pos, True)
        pos_scaled_global = translate_global_to_local(pos_scaled, reference_frame_rect, local_origin_offset, True)
        return (pos_scaled_global[0], pos_scaled_global[1])


def vector2_to_int_tuple(vector: Vector2) -> tuple:
    return int(vector.x), int(vector.y)
