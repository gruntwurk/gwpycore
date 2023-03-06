from typing import Tuple
import re

__all__ = [
    'color_parse',
    'color_hex_format',
    'as_color',
    'HTML_COLORS'
]

HTML_COLORS = {
    'aliceblue': (240, 248, 255),  # #F0F8FF
    'antiquewhite': (250, 235, 215),  # #FAEBD7
    'aqua': (0, 255, 255),  # #00FFFF (dup of CYAN)
    'aquamarine': (127, 255, 212),  # #7FFFD4
    'azure': (240, 255, 255),  # #F0FFFF
    'beige': (245, 245, 220),  # #F5F5DC
    'bisque': (255, 228, 196),  # #FFE4C4
    'black': (0, 0, 0),  # #000000
    'blanchedalmond': (255, 235, 205),  # #FFEBCD
    'blue': (0, 0, 255),  # #0000FF
    'blueviolet': (138, 43, 226),  # #8A2BE2
    'brown': (165, 42, 42),  # #A52A2A
    'burlywood': (222, 184, 135),  # #DEB887
    'cadetblue': (95, 158, 160),  # #5F9EA0
    'chartreuse': (127, 255, 0),  # #7FFF00
    'chocolate': (210, 105, 30),  # #D2691E
    'coral': (255, 127, 80),  # #FF7F50
    'cornflowerblue': (100, 149, 237),  # #6495ED
    'cornsilk': (255, 248, 220),  # #FFF8DC
    'crimson': (220, 20, 60),  # #DC143C
    'cyan': (0, 255, 255),  # #00FFFF
    'darkblue': (0, 0, 139),  # #00008B
    'darkcyan': (0, 139, 139),  # #008B8B
    'darkgoldenrod': (184, 134, 11),  # #B8860B
    'darkgray': (169, 169, 169),  # #A9A9A9
    'darkgreen': (0, 100, 0),  # #006400
    'darkkhaki': (189, 183, 107),  # #BDB76B
    'darkmagenta': (139, 0, 139),  # #8B008B
    'darkolivegreen': (85, 107, 47),  # #556B2F
    'darkorange': (255, 140, 0),  # #FF8C00
    'darkorchid': (153, 50, 204),  # #9932CC
    'darkred': (139, 0, 0),  # #8B0000
    'darksalmon': (233, 150, 122),  # #E9967A
    'darkseagreen': (143, 188, 143),  # #8FBC8F
    'darkslateblue': (72, 61, 139),  # #483D8B
    'darkslategray': (47, 79, 79),  # #2F4F4F
    'darkturquoise': (0, 206, 209),  # #00CED1
    'darkviolet': (148, 0, 211),  # #9400D3
    'deeppink': (255, 20, 147),  # #FF1493
    'deepskyblue': (0, 191, 255),  # #00BFFF
    'dimgray': (105, 105, 105),  # #696969
    'dodgerblue': (30, 144, 255),  # #1E90FF
    'firebrick': (178, 34, 34),  # #B22222
    'floralwhite': (255, 250, 240),  # #FFFAF0
    'forestgreen': (34, 139, 34),  # #228B22
    'fuchsia': (255, 0, 255),  # #FF00FF (dup of MAGENTA)
    'gainsboro': (220, 220, 220),  # #DCDCDC
    'ghostwhite': (248, 248, 255),  # #F8F8FF
    'gold': (255, 215, 0),  # #FFD700
    'goldenrod': (218, 165, 32),  # #DAA520
    'gray': (128, 128, 128),  # #808080
    'green': (0, 128, 0),  # #008000
    'greenyellow': (173, 255, 47),  # #ADFF2F
    'honeydew': (240, 255, 240),  # #F0FFF0
    'hotpink': (255, 105, 180),  # #FF69B4
    'indianred': (205, 92, 92),  # #CD5C5C
    'indigo': (75, 0, 130),  # #4B0082
    'ivory': (255, 255, 240),  # #FFFFF0
    'khaki': (240, 230, 140),  # #F0E68C
    'lavender': (230, 230, 250),  # #E6E6FA
    'lavenderblush': (255, 240, 245),  # #FFF0F5
    'lawngreen': (124, 252, 0),  # #7CFC00
    'lemonchiffon': (255, 250, 205),  # #FFFACD
    'lightblue': (173, 216, 230),  # #ADD8E6
    'lightcoral': (240, 128, 128),  # #F08080
    'lightcyan': (224, 255, 255),  # #E0FFFF
    'lightgoldenrodyellow': (250, 250, 210),  # #FAFAD2
    'lightgray': (211, 211, 211),  # #D3D3D3
    'lightgreen': (144, 238, 144),  # #90EE90
    'lightpink': (255, 182, 193),  # #FFB6C1
    'lightsalmon': (255, 160, 122),  # #FFA07A
    'lightseagreen': (32, 178, 170),  # #20B2AA
    'lightskyblue': (135, 206, 250),  # #87CEFA
    'lightslategray': (119, 136, 153),  # #778899
    'lightsteelblue': (176, 196, 222),  # #B0C4DE
    'lightyellow': (255, 255, 224),  # #FFFFE0
    'lime': (0, 255, 0),  # #00FF00
    'limegreen': (50, 205, 50),  # #32CD32
    'linen': (250, 240, 230),  # #FAF0E6
    'magenta': (255, 0, 255),  # #FF00FF
    'maroon': (128, 0, 0),  # #800000
    'mediumaquamarine': (102, 205, 170),  # #66CDAA
    'mediumblue': (0, 0, 205),  # #0000CD
    'mediumorchid': (186, 85, 211),  # #BA55D3
    'mediumpurple': (147, 112, 219),  # #9370DB
    'mediumseagreen': (60, 179, 113),  # #3CB371
    'mediumslateblue': (123, 104, 238),  # #7B68EE
    'mediumspringgreen': (0, 250, 154),  # #00FA9A
    'mediumturquoise': (72, 209, 204),  # #48D1CC
    'mediumvioletred': (199, 21, 133),  # #C71585
    'midnightblue': (25, 25, 112),  # #191970
    'mintcream': (245, 255, 250),  # #F5FFFA
    'mistyrose': (255, 228, 225),  # #FFE4E1
    'moccasin': (255, 228, 181),  # #FFE4B5
    'navajowhite': (255, 222, 173),  # #FFDEAD
    'navy': (0, 0, 128),  # #000080
    'oldlace': (253, 245, 230),  # #FDF5E6
    'olive': (128, 128, 0),  # #808000
    'olivedrab': (107, 142, 35),  # #6B8E23
    'orange': (255, 165, 0),  # #FFA500
    'orangered': (255, 69, 0),  # #FF4500
    'orchid': (218, 112, 214),  # #DA70D6
    'palegoldenrod': (238, 232, 170),  # #EEE8AA
    'palegreen': (152, 251, 152),  # #98FB98
    'paleturquoise': (175, 238, 238),  # #AFEEEE
    'palevioletred': (219, 112, 147),  # #DB7093
    'papayawhip': (255, 239, 213),  # #FFEFD5
    'peachpuff': (255, 218, 185),  # #FFDAB9
    'peru': (205, 133, 63),  # #CD853F
    'pink': (255, 192, 203),  # #FFC0CB
    'plum': (221, 160, 221),  # #DDA0DD
    'powderblue': (176, 224, 230),  # #B0E0E6
    'purple': (128, 0, 128),  # #800080
    'red': (255, 0, 0),  # #FF0000
    'rosybrown': (188, 143, 143),  # #BC8F8F
    'royalblue': (65, 105, 225),  # #4169E1
    'saddlebrown': (139, 69, 19),  # #8B4513
    'salmon': (250, 128, 114),  # #FA8072
    'sandybrown': (244, 164, 96),  # #F4A460
    'seagreen': (46, 139, 87),  # #2E8B57
    'seashell': (255, 245, 238),  # #FFF5EE
    'sienna': (160, 82, 45),  # #A0522D
    'silver': (192, 192, 192),  # #C0C0C0
    'skyblue': (135, 206, 235),  # #87CEEB
    'slateblue': (106, 90, 205),  # #6A5ACD
    'slategray': (112, 128, 144),  # #708090
    'snow': (255, 250, 250),  # #FFFAFA
    'springgreen': (0, 255, 127),  # #00FF7F
    'steelblue': (70, 130, 180),  # #4682B4
    'tan': (210, 180, 140),  # #D2B48C
    'teal': (0, 128, 128),  # #008080
    'thistle': (216, 191, 216),  # #D8BFD8
    'tomato': (255, 99, 71),  # #FF6347
    'turquoise': (64, 224, 208),  # #40E0D0
    'violet': (238, 130, 238),  # #EE82EE
    'wheat': (245, 222, 179),  # #F5DEB3
    'white': (255, 255, 255),  # #FFFFFF
    'whitesmoke': (245, 245, 245),  # #F5F5F5
    'yellow': (255, 255, 0),  # #FFFF00
    'yellowgreen': (154, 205, 50),  # #9ACD32
}


def color_parse(expr: any, names=HTML_COLORS) -> Tuple:
    """
    Parses the input/expression to create an RGB or an RGBA tuple.

    :param expr: Any of these:
        * A named color (any case) that is defined (as lower case) in the
          optional `names` dictionary -- in which case, the associated value
          is parsed instead. By default, these can be any of the 140 HTML
          color names.
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
    that it also (a) uses the `NamedColor` enum that is introduced there, and
    (b) works with float tuples (0.0 - 1.0) as well as int tuples (0-255).
    """
    if isinstance(expr, str) and (ex := expr.strip().casefold()) in names:
        expr = names[ex]

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

