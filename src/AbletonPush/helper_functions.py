def try_parse_int(s, base=10, val=None):
    """returns 'val' instead of throwing an exception when parsing fails"""
    try:
        return int(s, base)
    except ValueError:
        return val


def format_float_precision(input_float: float, precision: int):
    format_str = "{:." + str(precision) + "f}"
    return format_str.format(input_float)
