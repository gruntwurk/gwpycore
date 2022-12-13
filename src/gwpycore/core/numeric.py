import re
from typing import List, Tuple


__all__ = [
    "as_int",
    "as_float",
    "as_tuple",
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


def as_tuple(input: any) -> Tuple:
    """
    If input is a string, it's converted to a tuple (of strings). Enclosing parenthesis are optional.
    If input is already is a tuple, it's returned as is.
    If input is a list, it's converted to a tuple.
    Any other input is retuned as a 1-tuple.
    """
    if type(input) is Tuple:
        return input
    if type(input) is str:
        if m := re.match(r'^ *\((.*)\) *$', input):
            input = m.group(1)
        return tuple(input.split(','))
    if type(input) is List:
        return tuple(input)
    return (input,)


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
