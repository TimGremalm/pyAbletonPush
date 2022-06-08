def try_parse_int(s, base=10, val=None):
    """returns 'val' instead of throwing an exception when parsing fails"""
    try:
        return int(s, base)
    except ValueError:
        return val


def format_float_precision(input_float: float, precision: int):
    format_str = "{:." + str(precision) + "f}"
    return format_str.format(input_float)


def translate(value, left_min, left_max, right_min, right_max):
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)
