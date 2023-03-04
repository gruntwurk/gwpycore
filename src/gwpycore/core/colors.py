from typing import Tuple
import re

__all__ = [
    'color_parse',
    'color_hex_format',
    'as_color',
]


def color_parse(expr: any, names=None) -> Tuple:
    """
    Parses the input/expression to create an RGB 3-tuple (or 4-tuple). The input can be:

        * A key value of the optional names dictionary (e.g. a base16 scheme)
          -- in which case, the associated value is parsed instead.
        * Hex format (#ff0088, #ff008840) -- the leading hash is optional. (Returns a 3- or 4-tuple.)
        * A string with an RGB tuple "(255,0,136)" -- the parens are optional. (Returns a 3- or 4-tuple.)
        * A tuple (any count) -- simply passed thru.

    NOTE: The version of this function in `kivygw` is more comprehensive in
    that it also uses the NamedColor enum that is introduced there.
    """
    if names is None:
        names = {}
    if isinstance(expr, Tuple):
        return expr

    if isinstance(expr, str) and expr in names:
        expr = names[expr]

    if not isinstance(expr, str):
        return None

    color = None
    expr = re.sub(r"[^#0-9a-fA-F,]", "", expr)
    if m := re.match(r"#?([0-9a-fA-F]{6,8})", expr):
        b = bytes.fromhex(m[1])
        color = tuple(int(x) for x in b)
    else:
        parts = expr.split(",")
        if len(parts) >= 3:
            color = tuple(int(x) for x in parts)

    return color


def color_hex_format(int_tuple) -> str:
    '''Returns color in hex format'''
    if len(int_tuple) == 3:
        return '#{:02X}{:02X}{:02X}'.format(*int_tuple)
    elif len(int_tuple) == 4:
        return '#{:02X}{:02X}{:02X}{:02X}'.format(*int_tuple)
    return ''


def as_color(input: any) -> Tuple:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    RGB tuples. Either a 3-tuple or a 4-tuple will be returned, depending on
    the input.

    A color (as configured) can be represented in hex format e.g. #ff0088 or
    #ff008840, or a tuple e.g. (255,0,136) or (255,0,136,40), or the color
    name (e.g. SKYBLUE4) accordibng to our `NamedColor` enum (550 enumerated
    colors). The leading number-sign (#) is optional for hex format. Parens
    are optional for RGB tuples. All settings are case-insensitive.
    """
    return color_parse(input)

