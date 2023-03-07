from PIL.ImageColor import colormap
from typing import Tuple
import re

__all__ = [
    'color_parse',
    'color_hex_format',
    'as_color',
]


def color_parse(expr: any, colormap2=None) -> Tuple:
    """
    Parses the input/expression to create an RGB or an RGBA int tuple.

    :param expr: Any of these:
        * A named color (any case) from the list of 140 HTML/X11 color names
          (with the 7 gray/grey colors spelled either way), as defined by
          `PIL.ImageColor.colormap`.
        * A named color (any case) that is defined (as lower case) in the
          optional `colormap2` dictionary -- in which case, the associated value
          is parsed instead.
        * Hex format `str` (#ff0088, #ff008840) -- the leading hash is optional.
        * A `str` with an RGB tuple "(255,0,136)" or an RGBA tuple
          "(255,0,136,48)" -- the parens are optional.
        * A tuple (any count) -- simply passed thru (without any checks on
          whether the tuple actually represents an RGB or RGBA color).

    :param names: (Optional) A dictionary of named colors (e.g. the colors of
        a syntax highlight scheme by purpose). The associated value can be
        expressed in any form accepted by `expr` (but use a tuple of ints for
        efficiency). Defaults to the 140 standard HTML colors ('red',
        'springgreen', etc.). NOTE: The keys must be lower case.

    :return: A 3- or 4-tuple of ints (0-255), depending on the `expr`.

    NOTE: The version of this function in `kivygw` is more comprehensive in
    that it uses the `NamedColor` enum that is introduced there, and
    (b) works with float tuples (0.0 - 1.0) as well as int tuples (0-255).

    See also: `PIL.ImageColor.getrgb()` and `PIL.ImageColor.getcolor()`.
    See also: `ReportLib` also has a set of color processing utilities.
    See also: `colorsys` (python build-in library) for converting between
    color system (e.g. RGB -> HSV).
    """
    if isinstance(expr, str):
        expr = expr.strip().casefold()
        if colormap2 and expr in colormap2:
            expr = colormap2[expr]

    if isinstance(expr, str):
        expr = expr.strip().casefold()
        if expr in colormap:
            expr = colormap[expr]

    if isinstance(expr, Tuple):
        return expr

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

