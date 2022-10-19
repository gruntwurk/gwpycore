import re


__all__ = [
    "as_int",
    "as_float",
    "next_in_range",
]


def as_int(input: any) -> int:
    """
    Converts a string to an int. Forgiving of strings that have a decimal point
    as long as it's only followed by zeros.
    """
    if type(input) == str:
        input = re.sub(r"\.0*$", "", input.strip())
    return int(input)


def as_float(input: any) -> int:
    """
    Converts a string to a float. Same as just calling float(input). This is
    here just to be consistent with all of the other as_X functions.
    """
    return float(input)


def next_in_range(index, max_value, min_value=0, increment=1) -> int:
    """
    Increments an index while keeping it in range.
    """

    index += increment
    if index > max_value:
        index = min_value
    if index < min_value:
        index = max_value
    return index
