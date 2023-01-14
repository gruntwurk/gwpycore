import re
from typing import List, Tuple


__all__ = [
    "as_int",
    "as_float",
    "as_tuple",
    "next_in_range",
    "round_base",
]


def as_int(input_str: any) -> int:
    """
    Converts a string to an int. Forgiving of strings that have a decimal point
    as long as it's only followed by zeros.
    """
    if type(input_str) == str:
        input_str = re.sub(r"\.0*$", "", input_str.strip())
    return int(input_str)


def as_float(input: any) -> int:
    """
    Converts a string to a float. Same as just calling float(input). This is
    here just to be consistent with all of the other as_X functions.
    """
    return float(input)


def as_tuple(input_any: any) -> Tuple:
    """
    If input is a string, it's converted to a tuple (of strings). Enclosing parenthesis are optional.
    If input is already is a tuple, it's returned as is.
    If input is a list, it's converted to a tuple.
    Any other input is retuned as a 1-tuple.
    """
    if type(input_any) is Tuple:
        return input_any
    if type(input_any) is str:
        if m := re.match(r'^ *\((.*)\) *$', input_any):
            input_any = m[1]
        return tuple(input_any.split(','))
    return tuple(input_any) if type(input_any) is List else (input_any, )


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


def round_base(x, base=5):
    """
    Rounds a number to the nearest base number.

    :param x: the raw number to be rounded
    :param base: the base (increment), defaults to 5
    """
    return base * round(x/base)