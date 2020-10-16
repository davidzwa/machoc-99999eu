PIXELS_PER_METER = 10


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
