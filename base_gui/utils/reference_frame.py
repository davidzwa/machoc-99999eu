from pygame import Vector2

PIXELS_PER_METER = 20


# This function serves as reference frame scaling (pixels/meter)
def scale_pixels_to_meters(value, reverse=False):
    if not reverse:
        return value / PIXELS_PER_METER
    else:
        return int(value * PIXELS_PER_METER)


def scale_tuple_pix2meter(coord, reverse=False):
    return (
        scale_pixels_to_meters(coord[0], reverse),
        scale_pixels_to_meters(coord[1], reverse)
    )


# This function serves as reference frame translation
def translate_global_to_local(position, reference_frame_rect, reverse=False):
    if not reverse:
        return (position[0] - reference_frame_rect.left, position[1] - reference_frame_rect.top)
    else:
        return (position[0] + reference_frame_rect.left, position[1] + reference_frame_rect.top)


def vector2_global_to_local(vector: Vector2, reference_frame_rect, reverse: bool = False):
    if not reverse:
        pos = (vector.x, vector.y)
        pos_transformed_local = scale_tuple_pix2meter(
            translate_global_to_local(pos, reference_frame_rect))
        return Vector2(pos_transformed_local)
    else:
        pos = (vector.x, vector.y)
        pos_scaled = scale_tuple_pix2meter(pos, True)
        pos_scaled_global = translate_global_to_local(pos_scaled, reference_frame_rect, True)
        return Vector2(pos_scaled_global)


def vector2_to_int_tuple(vector: Vector2) -> tuple:
    return int(vector.x), int(vector.y)
