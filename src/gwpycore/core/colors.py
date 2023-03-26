from enum import unique
from typing import List
import re
import math
from colorsys import hsv_to_rgb, rgb_to_hsv

from .enums import GWEnum


__all__ = [
    'HUE_NAMES',
    'NamedColor',
    'color_parse',
    'float_color',
    'float_tuple',
    'int_color',
    'int_tuple',
    'is_color',
    'is_float_tuple',
    'color_brightness',
    'color_subdued',
    'color_darker',
    'color_monochrome',
    'color_hex_format',
    'color_lighter',
    'color_outline',
    'color_complementary',
    'color_distance',
    'as_color',
    'as_named_color',
]

STANDARD = True
EXTRA = False
# Named positions on the color wheel in degrees
HUE_NAMES = {
    -1: 'grayscale',
    0: 'red',
    30: 'redorange',
    60: 'orange',
    90: 'yelloworange',
    120: 'yellow',
    150: 'yellowgreen',
    180: 'green',
    210: 'bluegreen',
    240: 'blue',
    270: 'blueviolet',
    300: 'violet',
    330: 'redviolet',
}


# ############################################################################
#                                                            NamedColor (enum)
# ############################################################################

@unique
class NamedColor(GWEnum):
    """
    An enumeration of 550+ specific colors, including the 140 standard HTML
    colors names (https://www.w3.org/TR/SVG11/types.html#ColorKeywords)
    as RGB tuples(0..256, 0..256,0..256), but also available
    as Kivy-style float (0.0 - 1.0) tuples.

    NOTE: The Kivy ColorProperty understands the 140 standard HTML names
    directly, but only in lower case. In a KV file, the color name must
    be quoted (e.g. Background_color: 'aqua').

    NamedColor.AZURE.hex_format() == #F0FFFF
    NamedColor.AZURE.float_tuple() == (0.0,0.0,0.0,1.0)
    NamedColor.AZURE.float_tuple(alpha=0.5) == (0.0,0.0,0.0,0.5)
    NamedColor.by_name("azure") == NamedColor.AZURE
    NamedColor.by_name("nosuch") == None
    NamedColor.by_value("#F0FFFF") == NamedColor.AZURE # exact match
    NamedColor.by_value("F0FFFF") == NamedColor.AZURE # exact match
    NamedColor.by_value(((240, 255, 255), STANDARD)) == NamedColor.AZURE1 # exact match
    NamedColor.by_value(((241, 254, 250), STANDARD)) == NamedColor.AZURE1 # (being the closest match)
    """

    # REDS (each section is roughly in order of light to dark)

    LIGHTSALMON = ((255, 160, 122), STANDARD)  # #FFA07A
    DARKSALMON = ((233, 150, 122), STANDARD)  # #E9967A
    LIGHTCORAL = ((240, 128, 128), STANDARD)  # #F08080
    SALMON = ((250, 128, 114), STANDARD)  # #FA8072
    INDIANRED = ((205, 92, 92), STANDARD)  # #CD5C5C
    CRIMSON = ((220, 20, 60), STANDARD)  # #DC143C
    RED = ((255, 0, 0), STANDARD)  # #FF0000
    FIREBRICK = ((178, 34, 34), STANDARD)  # #B22222
    DARKRED = ((139, 0, 0), STANDARD)  # #8B0000
    MAROON = ((128, 0, 0), STANDARD)  # #800000

    # PINKS

    PINK = ((255, 192, 203), STANDARD)  # #FFC0CB
    LIGHTPINK = ((255, 182, 193), STANDARD)  # #FFB6C1
    HOTPINK = ((255, 105, 180), STANDARD)  # #FF69B4
    PALEVIOLETRED = ((219, 112, 147), STANDARD)  # #DB7093
    DEEPPINK = ((255, 20, 147), STANDARD)  # #FF1493
    MEDIUMVIOLETRED = ((199, 21, 133), STANDARD)  # #C71585

    # ORANGES

    CORAL = ((255, 127, 80), STANDARD)  # #FF7F50
    TOMATO = ((255, 99, 71), STANDARD)  # #FF6347
    ORANGE = ((255, 165, 0), STANDARD)  # #FFA500
    DARKORANGE = ((255, 140, 0), STANDARD)  # #FF8C00
    ORANGERED = ((255, 69, 0), STANDARD)  # #FF4500

    # YELLOWS

    LIGHTYELLOW = ((255, 255, 224), STANDARD)  # #FFFFE0
    LIGHTGOLDENRODYELLOW = ((250, 250, 210), STANDARD)  # #FAFAD2
    LEMONCHIFFON = ((255, 250, 205), STANDARD)  # #FFFACD
    PAPAYAWHIP = ((255, 239, 213), STANDARD)  # #FFEFD5
    MOCCASIN = ((255, 228, 181), STANDARD)  # #FFE4B5
    PEACHPUFF = ((255, 218, 185), STANDARD)  # #FFDAB9
    PALEGOLDENROD = ((238, 232, 170), STANDARD)  # #EEE8AA
    KHAKI = ((240, 230, 140), STANDARD)  # #F0E68C
    YELLOW = ((255, 255, 0), STANDARD)  # #FFFF00
    DARKKHAKI = ((189, 183, 107), STANDARD)  # #BDB76B
    GOLD = ((255, 215, 0), STANDARD)  # #FFD700

    # PURPLES

    LAVENDER = ((230, 230, 250), STANDARD)  # #E6E6FA
    THISTLE = ((216, 191, 216), STANDARD)  # #D8BFD8
    VIOLET = ((238, 130, 238), STANDARD)  # #EE82EE
    PLUM = ((221, 160, 221), STANDARD)  # #DDA0DD
    ORCHID = ((218, 112, 214), STANDARD)  # #DA70D6
    MAGENTA = ((255, 0, 255), STANDARD)  # #FF00FF
    FUCHSIA = ((255, 0, 254), STANDARD)  # nominally #FF00FF (dup of MAGENTA)
    MEDIUMORCHID = ((186, 85, 211), STANDARD)  # #BA55D3
    MEDIUMPURPLE = ((147, 112, 219), STANDARD)  # #9370DB
    DARKORCHID = ((153, 50, 204), STANDARD)  # #9932CC
    BLUEVIOLET = ((138, 43, 226), STANDARD)  # #8A2BE2
    DARKVIOLET = ((148, 0, 211), STANDARD)  # #9400D3
    DARKMAGENTA = ((139, 0, 139), STANDARD)  # #8B008B
    PURPLE = ((128, 0, 128), STANDARD)  # #800080
    INDIGO = ((75, 0, 130), STANDARD)  # #4B0082

    # GREENS

    PALEGREEN = ((152, 251, 152), STANDARD)  # #98FB98
    LIGHTGREEN = ((144, 238, 144), STANDARD)  # #90EE90
    MEDIUMAQUAMARINE = ((102, 205, 170), STANDARD)  # #66CDAA
    GREENYELLOW = ((173, 255, 47), STANDARD)  # #ADFF2F
    DARKSEAGREEN = ((143, 188, 143), STANDARD)  # #8FBC8F
    YELLOWGREEN = ((154, 205, 50), STANDARD)  # #9ACD32
    MEDIUMSPRINGGREEN = ((0, 250, 154), STANDARD)  # #00FA9A
    SPRINGGREEN = ((0, 255, 127), STANDARD)  # #00FF7F
    CHARTREUSE = ((127, 255, 0), STANDARD)  # #7FFF00
    LIGHTSEAGREEN = ((32, 178, 170), STANDARD)  # #20B2AA
    LAWNGREEN = ((124, 252, 0), STANDARD)  # #7CFC00
    MEDIUMSEAGREEN = ((60, 179, 113), STANDARD)  # #3CB371
    LIMEGREEN = ((50, 205, 50), STANDARD)  # #32CD32
    OLIVEDRAB = ((107, 142, 35), STANDARD)  # #6B8E23
    DARKCYAN = ((0, 139, 139), STANDARD)  # #008B8B
    SEAGREEN = ((46, 139, 87), STANDARD)  # #2E8B57
    TEAL = ((0, 128, 128), STANDARD)  # #008080
    OLIVE = ((128, 128, 0), STANDARD)  # #808000
    LIME = ((0, 255, 0), STANDARD)  # #00FF00
    DARKOLIVEGREEN = ((85, 107, 47), STANDARD)  # #556B2F
    FORESTGREEN = ((34, 139, 34), STANDARD)  # #228B22
    GREEN = ((0, 128, 0), STANDARD)  # #008000
    DARKGREEN = ((0, 100, 0), STANDARD)  # #006400

    # BLUES

    LIGHTCYAN = ((224, 255, 255), STANDARD)  # #E0FFFF
    PALETURQUOISE = ((175, 238, 238), STANDARD)  # #AFEEEE
    POWDERBLUE = ((176, 224, 230), STANDARD)  # #B0E0E6
    LIGHTBLUE = ((173, 216, 230), STANDARD)  # #ADD8E6
    LIGHTSTEELBLUE = ((176, 196, 222), STANDARD)  # #B0C4DE
    AQUAMARINE = ((127, 255, 212), STANDARD)  # #7FFFD4
    LIGHTSKYBLUE = ((135, 206, 250), STANDARD)  # #87CEFA
    SKYBLUE = ((135, 206, 235), STANDARD)  # #87CEEB
    CYAN = ((0, 255, 255), STANDARD)  # #00FFFF
    AQUA = ((0, 255, 254), STANDARD)  # nominally #00FFFF (dup of CYAN)
    TURQUOISE = ((64, 224, 208), STANDARD)  # #40E0D0
    CORNFLOWERBLUE = ((100, 149, 237), STANDARD)  # #6495ED
    MEDIUMTURQUOISE = ((72, 209, 204), STANDARD)  # #48D1CC
    MEDIUMSLATEBLUE = ((123, 104, 238), STANDARD)  # #7B68EE
    DEEPSKYBLUE = ((0, 191, 255), STANDARD)  # #00BFFF
    DODGERBLUE = ((30, 144, 255), STANDARD)  # #1E90FF
    DARKTURQUOISE = ((0, 206, 209), STANDARD)  # #00CED1
    CADETBLUE = ((95, 158, 160), STANDARD)  # #5F9EA0
    SLATEBLUE = ((106, 90, 205), STANDARD)  # #6A5ACD
    ROYALBLUE = ((65, 105, 225), STANDARD)  # #4169E1
    STEELBLUE = ((70, 130, 180), STANDARD)  # #4682B4
    DARKSLATEBLUE = ((72, 61, 139), STANDARD)  # #483D8B
    BLUE = ((0, 0, 255), STANDARD)  # #0000FF
    MEDIUMBLUE = ((0, 0, 205), STANDARD)  # #0000CD
    MIDNIGHTBLUE = ((25, 25, 112), STANDARD)  # #191970
    DARKBLUE = ((0, 0, 139), STANDARD)  # #00008B
    NAVY = ((0, 0, 128), STANDARD)  # #000080

    # BROWNS

    CORNSILK = ((255, 248, 220), STANDARD)  # #FFF8DC
    BLANCHEDALMOND = ((255, 235, 205), STANDARD)  # #FFEBCD
    BISQUE = ((255, 228, 196), STANDARD)  # #FFE4C4
    NAVAJOWHITE = ((255, 222, 173), STANDARD)  # #FFDEAD
    WHEAT = ((245, 222, 179), STANDARD)  # #F5DEB3
    BURLYWOOD = ((222, 184, 135), STANDARD)  # #DEB887
    TAN = ((210, 180, 140), STANDARD)  # #D2B48C
    SANDYBROWN = ((244, 164, 96), STANDARD)  # #F4A460
    ROSYBROWN = ((188, 143, 143), STANDARD)  # #BC8F8F
    GOLDENROD = ((218, 165, 32), STANDARD)  # #DAA520
    PERU = ((205, 133, 63), STANDARD)  # #CD853F
    CHOCOLATE = ((210, 105, 30), STANDARD)  # #D2691E
    DARKGOLDENROD = ((184, 134, 11), STANDARD)  # #B8860B
    SIENNA = ((160, 82, 45), STANDARD)  # #A0522D
    BROWN = ((165, 42, 42), STANDARD)  # #A52A2A
    SADDLEBROWN = ((139, 69, 19), STANDARD)  # #8B4513

    # WHITES

    WHITE = ((255, 255, 255), STANDARD)  # #FFFFFF
    SNOW = ((255, 250, 250), STANDARD)  # #FFFAFA
    MINTCREAM = ((245, 255, 250), STANDARD)  # #F5FFFA
    IVORY = ((255, 255, 240), STANDARD)  # #FFFFF0
    GHOSTWHITE = ((248, 248, 255), STANDARD)  # #F8F8FF
    AZURE = ((240, 255, 255), STANDARD)  # #F0FFFF
    FLORALWHITE = ((255, 250, 240), STANDARD)  # #FFFAF0
    ALICEBLUE = ((240, 248, 255), STANDARD)  # #F0F8FF
    SEASHELL = ((255, 245, 238), STANDARD)  # #FFF5EE
    LAVENDERBLUSH = ((255, 240, 245), STANDARD)  # #FFF0F5
    WHITESMOKE = ((245, 245, 245), STANDARD)  # #F5F5F5
    HONEYDEW = ((240, 255, 240), STANDARD)  # #F0FFF0
    OLDLACE = ((253, 245, 230), STANDARD)  # #FDF5E6
    LINEN = ((250, 240, 230), STANDARD)  # #FAF0E6
    MISTYROSE = ((255, 228, 225), STANDARD)  # #FFE4E1
    BEIGE = ((245, 245, 220), STANDARD)  # #F5F5DC
    ANTIQUEWHITE = ((250, 235, 215), STANDARD)  # #FAEBD7

    # GRAYS

    GAINSBORO = ((220, 220, 220), STANDARD)  # #DCDCDC
    LIGHTGRAY = ((211, 211, 211), STANDARD)  # #D3D3D3
    SILVER = ((192, 192, 192), STANDARD)  # #C0C0C0
    DARKGRAY = ((169, 169, 169), STANDARD)  # #A9A9A9
    LIGHTSLATEGRAY = ((119, 136, 153), STANDARD)  # #778899
    SLATEGRAY = ((112, 128, 144), STANDARD)  # #708090
    GRAY = ((128, 128, 128), STANDARD)  # #808080
    DIMGRAY = ((105, 105, 105), STANDARD)  # #696969
    DARKSLATEGRAY = ((47, 79, 79), STANDARD)  # #2F4F4F
    BLACK = ((0, 0, 0), STANDARD)  # #000000

    # 448 Additional (Non-Standard) Color Names

    AQUAMARINE2 = ((118, 238, 198), EXTRA)
    AQUAMARINE4 = ((69, 139, 116), EXTRA)
    ANTIQUEWHITE1 = ((255, 239, 219), EXTRA)
    ANTIQUEWHITE2 = ((238, 223, 204), EXTRA)
    ANTIQUEWHITE3 = ((205, 192, 176), EXTRA)
    ANTIQUEWHITE4 = ((139, 131, 120), EXTRA)
    AZURE2 = ((224, 238, 238), EXTRA)
    AZURE3 = ((193, 205, 205), EXTRA)
    AZURE4 = ((131, 139, 139), EXTRA)
    BANANA = ((227, 207, 87), EXTRA)
    BISQUE2 = ((238, 213, 183), EXTRA)
    BISQUE3 = ((205, 183, 158), EXTRA)
    BISQUE4 = ((139, 125, 107), EXTRA)
    BLUE2 = ((0, 0, 238), EXTRA)
    BRICK = ((156, 102, 31), EXTRA)
    BROWN1 = ((255, 64, 64), EXTRA)
    BROWN2 = ((238, 59, 59), EXTRA)
    BROWN3 = ((205, 51, 51), EXTRA)
    BROWN4 = ((139, 35, 35), EXTRA)
    BURLYWOOD1 = ((255, 211, 155), EXTRA)
    BURLYWOOD2 = ((238, 197, 145), EXTRA)
    BURLYWOOD3 = ((205, 170, 125), EXTRA)
    BURLYWOOD4 = ((139, 115, 85), EXTRA)
    BURNTSIENNA = ((138, 54, 15), EXTRA)
    BURNTUMBER = ((138, 51, 36), EXTRA)
    CADETBLUE1 = ((152, 245, 255), EXTRA)
    CADETBLUE2 = ((142, 229, 238), EXTRA)
    CADETBLUE3 = ((122, 197, 205), EXTRA)
    CADETBLUE4 = ((83, 134, 139), EXTRA)
    CADMIUMORANGE = ((255, 97, 3), EXTRA)
    CADMIUMYELLOW = ((255, 153, 18), EXTRA)
    CARROT = ((237, 145, 33), EXTRA)
    CHARTREUSE2 = ((118, 238, 0), EXTRA)
    CHARTREUSE3 = ((102, 205, 0), EXTRA)
    CHARTREUSE4 = ((69, 139, 0), EXTRA)
    CHOCOLATE1 = ((255, 127, 36), EXTRA)
    CHOCOLATE2 = ((238, 118, 33), EXTRA)
    CHOCOLATE3 = ((205, 102, 29), EXTRA)
    COBALT = ((61, 89, 171), EXTRA)
    COBALTGREEN = ((61, 145, 64), EXTRA)
    COLDGREY = ((128, 138, 135), EXTRA)
    CORAL1 = ((255, 114, 86), EXTRA)
    CORAL2 = ((238, 106, 80), EXTRA)
    CORAL3 = ((205, 91, 69), EXTRA)
    CORAL4 = ((139, 62, 47), EXTRA)
    CORNSILK2 = ((238, 232, 205), EXTRA)
    CORNSILK3 = ((205, 200, 177), EXTRA)
    CORNSILK4 = ((139, 136, 120), EXTRA)
    CYAN2 = ((0, 238, 238), EXTRA)
    CYAN3 = ((0, 205, 205), EXTRA)
    DARKGOLDENROD1 = ((255, 185, 15), EXTRA)
    DARKGOLDENROD2 = ((238, 173, 14), EXTRA)
    DARKGOLDENROD3 = ((205, 149, 12), EXTRA)
    DARKGOLDENROD4 = ((139, 101, 8), EXTRA)
    DARKOLIVEGREEN1 = ((202, 255, 112), EXTRA)
    DARKOLIVEGREEN2 = ((188, 238, 104), EXTRA)
    DARKOLIVEGREEN3 = ((162, 205, 90), EXTRA)
    DARKOLIVEGREEN4 = ((110, 139, 61), EXTRA)
    DARKORANGE1 = ((255, 127, 0), EXTRA)
    DARKORANGE2 = ((238, 118, 0), EXTRA)
    DARKORANGE3 = ((205, 102, 0), EXTRA)
    DARKORANGE4 = ((139, 69, 0), EXTRA)
    DARKORCHID1 = ((191, 62, 255), EXTRA)
    DARKORCHID2 = ((178, 58, 238), EXTRA)
    DARKORCHID3 = ((154, 50, 205), EXTRA)
    DARKORCHID4 = ((104, 34, 139), EXTRA)
    DARKSEAGREEN1 = ((193, 255, 193), EXTRA)
    DARKSEAGREEN2 = ((180, 238, 180), EXTRA)
    DARKSEAGREEN3 = ((155, 205, 155), EXTRA)
    DARKSEAGREEN4 = ((105, 139, 105), EXTRA)
    DARKSLATEGRAY1 = ((151, 255, 255), EXTRA)
    DARKSLATEGRAY2 = ((141, 238, 238), EXTRA)
    DARKSLATEGRAY3 = ((121, 205, 205), EXTRA)
    DARKSLATEGRAY4 = ((82, 139, 139), EXTRA)
    DEEPPINK2 = ((238, 18, 137), EXTRA)
    DEEPPINK3 = ((205, 16, 118), EXTRA)
    DEEPPINK4 = ((139, 10, 80), EXTRA)
    DEEPSKYBLUE2 = ((0, 178, 238), EXTRA)
    DEEPSKYBLUE3 = ((0, 154, 205), EXTRA)
    DEEPSKYBLUE4 = ((0, 104, 139), EXTRA)
    DODGERBLUE2 = ((28, 134, 238), EXTRA)
    DODGERBLUE3 = ((24, 116, 205), EXTRA)
    DODGERBLUE4 = ((16, 78, 139), EXTRA)
    EGGSHELL = ((252, 230, 201), EXTRA)
    EMERALDGREEN = ((0, 201, 87), EXTRA)
    FIREBRICK1 = ((255, 48, 48), EXTRA)
    FIREBRICK2 = ((238, 44, 44), EXTRA)
    FIREBRICK3 = ((205, 38, 38), EXTRA)
    FIREBRICK4 = ((139, 26, 26), EXTRA)
    FLESH = ((255, 125, 64), EXTRA)
    GOLD2 = ((238, 201, 0), EXTRA)
    GOLD3 = ((205, 173, 0), EXTRA)
    GOLD4 = ((139, 117, 0), EXTRA)
    GOLDENROD1 = ((255, 193, 37), EXTRA)
    GOLDENROD2 = ((238, 180, 34), EXTRA)
    GOLDENROD3 = ((205, 155, 29), EXTRA)
    GOLDENROD4 = ((139, 105, 20), EXTRA)
    GRAY1 = ((3, 3, 3), EXTRA)
    GRAY2 = ((5, 5, 5), EXTRA)
    GRAY3 = ((8, 8, 8), EXTRA)
    GRAY4 = ((10, 10, 10), EXTRA)
    GRAY5 = ((13, 13, 13), EXTRA)
    GRAY6 = ((15, 15, 15), EXTRA)
    GRAY7 = ((18, 18, 18), EXTRA)
    GRAY8 = ((20, 20, 20), EXTRA)
    GRAY9 = ((23, 23, 23), EXTRA)
    GRAY10 = ((26, 26, 26), EXTRA)
    GRAY11 = ((28, 28, 28), EXTRA)
    GRAY12 = ((31, 31, 31), EXTRA)
    GRAY13 = ((33, 33, 33), EXTRA)
    GRAY14 = ((36, 36, 36), EXTRA)
    GRAY15 = ((38, 38, 38), EXTRA)
    GRAY16 = ((41, 41, 41), EXTRA)
    GRAY17 = ((43, 43, 43), EXTRA)
    GRAY18 = ((46, 46, 46), EXTRA)
    GRAY19 = ((48, 48, 48), EXTRA)
    GRAY20 = ((51, 51, 51), EXTRA)
    GRAY21 = ((54, 54, 54), EXTRA)
    GRAY22 = ((56, 56, 56), EXTRA)
    GRAY23 = ((59, 59, 59), EXTRA)
    GRAY24 = ((61, 61, 61), EXTRA)
    GRAY25 = ((64, 64, 64), EXTRA)
    GRAY26 = ((66, 66, 66), EXTRA)
    GRAY27 = ((69, 69, 69), EXTRA)
    GRAY28 = ((71, 71, 71), EXTRA)
    GRAY29 = ((74, 74, 74), EXTRA)
    GRAY30 = ((77, 77, 77), EXTRA)
    GRAY31 = ((79, 79, 79), EXTRA)
    GRAY32 = ((82, 82, 82), EXTRA)
    GRAY33 = ((84, 84, 84), EXTRA)
    GRAY34 = ((87, 87, 87), EXTRA)
    GRAY35 = ((89, 89, 89), EXTRA)
    GRAY36 = ((92, 92, 92), EXTRA)
    GRAY37 = ((94, 94, 94), EXTRA)
    GRAY38 = ((97, 97, 97), EXTRA)
    GRAY39 = ((99, 99, 99), EXTRA)
    GRAY40 = ((102, 102, 102), EXTRA)
    GRAY42 = ((107, 107, 107), EXTRA)
    GRAY43 = ((110, 110, 110), EXTRA)
    GRAY44 = ((112, 112, 112), EXTRA)
    GRAY45 = ((115, 115, 115), EXTRA)
    GRAY46 = ((117, 117, 117), EXTRA)
    GRAY47 = ((120, 120, 120), EXTRA)
    GRAY48 = ((122, 122, 122), EXTRA)
    GRAY49 = ((125, 125, 125), EXTRA)
    GRAY50 = ((127, 127, 127), EXTRA)
    GRAY51 = ((130, 130, 130), EXTRA)
    GRAY52 = ((133, 133, 133), EXTRA)
    GRAY53 = ((135, 135, 135), EXTRA)
    GRAY54 = ((138, 138, 138), EXTRA)
    GRAY55 = ((140, 140, 140), EXTRA)
    GRAY56 = ((143, 143, 143), EXTRA)
    GRAY57 = ((145, 145, 145), EXTRA)
    GRAY58 = ((148, 148, 148), EXTRA)
    GRAY59 = ((150, 150, 150), EXTRA)
    GRAY60 = ((153, 153, 153), EXTRA)
    GRAY61 = ((156, 156, 156), EXTRA)
    GRAY62 = ((158, 158, 158), EXTRA)
    GRAY63 = ((161, 161, 161), EXTRA)
    GRAY64 = ((163, 163, 163), EXTRA)
    GRAY65 = ((166, 166, 166), EXTRA)
    GRAY66 = ((168, 168, 168), EXTRA)
    GRAY67 = ((171, 171, 171), EXTRA)
    GRAY68 = ((173, 173, 173), EXTRA)
    GRAY69 = ((176, 176, 176), EXTRA)
    GRAY70 = ((179, 179, 179), EXTRA)
    GRAY71 = ((181, 181, 181), EXTRA)
    GRAY72 = ((184, 184, 184), EXTRA)
    GRAY73 = ((186, 186, 186), EXTRA)
    GRAY74 = ((189, 189, 189), EXTRA)
    GRAY75 = ((191, 191, 191), EXTRA)
    GRAY76 = ((194, 194, 194), EXTRA)
    GRAY77 = ((196, 196, 196), EXTRA)
    GRAY78 = ((199, 199, 199), EXTRA)
    GRAY79 = ((201, 201, 201), EXTRA)
    GRAY80 = ((204, 204, 204), EXTRA)
    GRAY81 = ((207, 207, 207), EXTRA)
    GRAY82 = ((209, 209, 209), EXTRA)
    GRAY83 = ((212, 212, 212), EXTRA)
    GRAY84 = ((214, 214, 214), EXTRA)
    GRAY85 = ((217, 217, 217), EXTRA)
    GRAY86 = ((219, 219, 219), EXTRA)
    GRAY87 = ((222, 222, 222), EXTRA)
    GRAY88 = ((224, 224, 224), EXTRA)
    GRAY89 = ((227, 227, 227), EXTRA)
    GRAY90 = ((229, 229, 229), EXTRA)
    GRAY91 = ((232, 232, 232), EXTRA)
    GRAY92 = ((235, 235, 235), EXTRA)
    GRAY93 = ((237, 237, 237), EXTRA)
    GRAY94 = ((240, 240, 240), EXTRA)
    GRAY95 = ((242, 242, 242), EXTRA)
    GRAY97 = ((247, 247, 247), EXTRA)
    GRAY98 = ((250, 250, 250), EXTRA)
    GRAY99 = ((252, 252, 252), EXTRA)
    GREEN2 = ((0, 238, 0), EXTRA)
    GREEN3 = ((0, 205, 0), EXTRA)
    GREEN4 = ((0, 139, 0), EXTRA)
    HONEYDEW2 = ((224, 238, 224), EXTRA)
    HONEYDEW3 = ((193, 205, 193), EXTRA)
    HONEYDEW4 = ((131, 139, 131), EXTRA)
    HOTPINK1 = ((255, 110, 180), EXTRA)
    HOTPINK2 = ((238, 106, 167), EXTRA)
    HOTPINK3 = ((205, 96, 144), EXTRA)
    HOTPINK4 = ((139, 58, 98), EXTRA)
    INDIANRED1 = ((255, 106, 106), EXTRA)
    INDIANRED2 = ((238, 99, 99), EXTRA)
    INDIANRED3 = ((205, 85, 85), EXTRA)
    INDIANRED4 = ((139, 58, 58), EXTRA)
    IVORY2 = ((238, 238, 224), EXTRA)
    IVORY3 = ((205, 205, 193), EXTRA)
    IVORY4 = ((139, 139, 131), EXTRA)
    IVORYBLACK = ((41, 36, 33), EXTRA)
    KHAKI1 = ((255, 246, 143), EXTRA)
    KHAKI2 = ((238, 230, 133), EXTRA)
    KHAKI3 = ((205, 198, 115), EXTRA)
    KHAKI4 = ((139, 134, 78), EXTRA)
    LAVENDERBLUSH2 = ((238, 224, 229), EXTRA)
    LAVENDERBLUSH3 = ((205, 193, 197), EXTRA)
    LAVENDERBLUSH4 = ((139, 131, 134), EXTRA)
    LEMONCHIFFON2 = ((238, 233, 191), EXTRA)
    LEMONCHIFFON3 = ((205, 201, 165), EXTRA)
    LEMONCHIFFON4 = ((139, 137, 112), EXTRA)
    LIGHTBLUE1 = ((191, 239, 255), EXTRA)
    LIGHTBLUE2 = ((178, 223, 238), EXTRA)
    LIGHTBLUE3 = ((154, 192, 205), EXTRA)
    LIGHTBLUE4 = ((104, 131, 139), EXTRA)
    LIGHTCYAN2 = ((209, 238, 238), EXTRA)
    LIGHTCYAN3 = ((180, 205, 205), EXTRA)
    LIGHTCYAN4 = ((122, 139, 139), EXTRA)
    LIGHTGOLDENROD1 = ((255, 236, 139), EXTRA)
    LIGHTGOLDENROD2 = ((238, 220, 130), EXTRA)
    LIGHTGOLDENROD3 = ((205, 190, 112), EXTRA)
    LIGHTGOLDENROD4 = ((139, 129, 76), EXTRA)
    LIGHTPINK1 = ((255, 174, 185), EXTRA)
    LIGHTPINK2 = ((238, 162, 173), EXTRA)
    LIGHTPINK3 = ((205, 140, 149), EXTRA)
    LIGHTPINK4 = ((139, 95, 101), EXTRA)
    LIGHTSALMON2 = ((238, 149, 114), EXTRA)
    LIGHTSALMON3 = ((205, 129, 98), EXTRA)
    LIGHTSALMON4 = ((139, 87, 66), EXTRA)
    LIGHTSKYBLUE1 = ((176, 226, 255), EXTRA)
    LIGHTSKYBLUE2 = ((164, 211, 238), EXTRA)
    LIGHTSKYBLUE3 = ((141, 182, 205), EXTRA)
    LIGHTSKYBLUE4 = ((96, 123, 139), EXTRA)
    LIGHTSLATEBLUE = ((132, 112, 255), EXTRA)
    LIGHTSTEELBLUE1 = ((202, 225, 255), EXTRA)
    LIGHTSTEELBLUE2 = ((188, 210, 238), EXTRA)
    LIGHTSTEELBLUE3 = ((162, 181, 205), EXTRA)
    LIGHTSTEELBLUE4 = ((110, 123, 139), EXTRA)
    LIGHTYELLOW2 = ((238, 238, 209), EXTRA)
    LIGHTYELLOW3 = ((205, 205, 180), EXTRA)
    LIGHTYELLOW4 = ((139, 139, 122), EXTRA)
    MAGENTA2 = ((238, 0, 238), EXTRA)
    MAGENTA3 = ((205, 0, 205), EXTRA)
    MANGANESEBLUE = ((3, 168, 158), EXTRA)
    MAROON1 = ((255, 52, 179), EXTRA)
    MAROON2 = ((238, 48, 167), EXTRA)
    MAROON3 = ((205, 41, 144), EXTRA)
    MAROON4 = ((139, 28, 98), EXTRA)
    MEDIUMORCHID1 = ((224, 102, 255), EXTRA)
    MEDIUMORCHID2 = ((209, 95, 238), EXTRA)
    MEDIUMORCHID3 = ((180, 82, 205), EXTRA)
    MEDIUMORCHID4 = ((122, 55, 139), EXTRA)
    MEDIUMPURPLE1 = ((171, 130, 255), EXTRA)
    MEDIUMPURPLE2 = ((159, 121, 238), EXTRA)
    MEDIUMPURPLE3 = ((137, 104, 205), EXTRA)
    MEDIUMPURPLE4 = ((93, 71, 139), EXTRA)
    MELON = ((227, 168, 105), EXTRA)
    MINT = ((189, 252, 201), EXTRA)
    MISTYROSE2 = ((238, 213, 210), EXTRA)
    MISTYROSE3 = ((205, 183, 181), EXTRA)
    MISTYROSE4 = ((139, 125, 123), EXTRA)
    NAVAJOWHITE2 = ((238, 207, 161), EXTRA)
    NAVAJOWHITE3 = ((205, 179, 139), EXTRA)
    NAVAJOWHITE4 = ((139, 121, 94), EXTRA)
    OLIVEDRAB1 = ((192, 255, 62), EXTRA)
    OLIVEDRAB2 = ((179, 238, 58), EXTRA)
    OLIVEDRAB4 = ((105, 139, 34), EXTRA)
    ORANGE2 = ((238, 154, 0), EXTRA)
    ORANGE3 = ((205, 133, 0), EXTRA)
    ORANGE4 = ((139, 90, 0), EXTRA)
    ORANGERED2 = ((238, 64, 0), EXTRA)
    ORANGERED3 = ((205, 55, 0), EXTRA)
    ORANGERED4 = ((139, 37, 0), EXTRA)
    ORCHID1 = ((255, 131, 250), EXTRA)
    ORCHID2 = ((238, 122, 233), EXTRA)
    ORCHID3 = ((205, 105, 201), EXTRA)
    ORCHID4 = ((139, 71, 137), EXTRA)
    PALEGREEN1 = ((154, 255, 154), EXTRA)
    PALEGREEN3 = ((124, 205, 124), EXTRA)
    PALEGREEN4 = ((84, 139, 84), EXTRA)
    PALETURQUOISE1 = ((187, 255, 255), EXTRA)
    PALETURQUOISE2 = ((174, 238, 238), EXTRA)
    PALETURQUOISE3 = ((150, 205, 205), EXTRA)
    PALETURQUOISE4 = ((102, 139, 139), EXTRA)
    PALEVIOLETRED1 = ((255, 130, 171), EXTRA)
    PALEVIOLETRED2 = ((238, 121, 159), EXTRA)
    PALEVIOLETRED3 = ((205, 104, 137), EXTRA)
    PALEVIOLETRED4 = ((139, 71, 93), EXTRA)
    PEACHPUFF2 = ((238, 203, 173), EXTRA)
    PEACHPUFF3 = ((205, 175, 149), EXTRA)
    PEACHPUFF4 = ((139, 119, 101), EXTRA)
    PEACOCK = ((51, 161, 201), EXTRA)
    PINK1 = ((255, 181, 197), EXTRA)
    PINK2 = ((238, 169, 184), EXTRA)
    PINK3 = ((205, 145, 158), EXTRA)
    PINK4 = ((139, 99, 108), EXTRA)
    PLUM1 = ((255, 187, 255), EXTRA)
    PLUM2 = ((238, 174, 238), EXTRA)
    PLUM3 = ((205, 150, 205), EXTRA)
    PLUM4 = ((139, 102, 139), EXTRA)
    PURPLE1 = ((155, 48, 255), EXTRA)
    PURPLE2 = ((145, 44, 238), EXTRA)
    PURPLE3 = ((125, 38, 205), EXTRA)
    PURPLE4 = ((85, 26, 139), EXTRA)
    RASPBERRY = ((135, 38, 87), EXTRA)
    RAWSIENNA = ((199, 97, 20), EXTRA)
    REBECCAPURPLE = ((102, 51, 153), EXTRA)  # #663399
    RED2 = ((238, 0, 0), EXTRA)
    RED3 = ((205, 0, 0), EXTRA)
    ROSYBROWN1 = ((255, 193, 193), EXTRA)
    ROSYBROWN2 = ((238, 180, 180), EXTRA)
    ROSYBROWN3 = ((205, 155, 155), EXTRA)
    ROSYBROWN4 = ((139, 105, 105), EXTRA)
    ROYALBLUE1 = ((72, 118, 255), EXTRA)
    ROYALBLUE2 = ((67, 110, 238), EXTRA)
    ROYALBLUE3 = ((58, 95, 205), EXTRA)
    ROYALBLUE4 = ((39, 64, 139), EXTRA)
    SALMON1 = ((255, 140, 105), EXTRA)
    SALMON2 = ((238, 130, 98), EXTRA)
    SALMON3 = ((205, 112, 84), EXTRA)
    SALMON4 = ((139, 76, 57), EXTRA)
    SAPGREEN = ((48, 128, 20), EXTRA)
    SEAGREEN1 = ((84, 255, 159), EXTRA)
    SEAGREEN2 = ((78, 238, 148), EXTRA)
    SEAGREEN3 = ((67, 205, 128), EXTRA)
    SEASHELL2 = ((238, 229, 222), EXTRA)
    SEASHELL3 = ((205, 197, 191), EXTRA)
    SEASHELL4 = ((139, 134, 130), EXTRA)
    SEPIA = ((94, 38, 18), EXTRA)
    SGIBEET = ((142, 56, 142), EXTRA)
    SGIBRIGHTGRAY = ((197, 193, 170), EXTRA)
    SGICHARTREUSE = ((113, 198, 113), EXTRA)
    SGIDARKGRAY = ((85, 85, 85), EXTRA)
    SGIGRAY12 = ((30, 30, 30), EXTRA)
    SGIGRAY16 = ((40, 40, 40), EXTRA)
    SGIGRAY32 = ((81, 81, 81), EXTRA)
    SGIGRAY36 = ((91, 91, 91), EXTRA)
    SGIGRAY52 = ((132, 132, 132), EXTRA)
    SGIGRAY56 = ((142, 142, 142), EXTRA)
    SGIGRAY72 = ((183, 183, 183), EXTRA)
    SGIGRAY76 = ((193, 193, 193), EXTRA)
    SGIGRAY92 = ((234, 234, 234), EXTRA)
    SGIGRAY96 = ((244, 244, 244), EXTRA)
    SGILIGHTBLUE = ((125, 158, 192), EXTRA)
    SGILIGHTGRAY = ((170, 170, 170), EXTRA)
    SGIOLIVEDRAB = ((142, 142, 56), EXTRA)
    SGISALMON = ((198, 113, 113), EXTRA)
    SGISLATEBLUE = ((113, 113, 198), EXTRA)
    SGITEAL = ((56, 142, 142), EXTRA)
    SIENNA1 = ((255, 130, 71), EXTRA)
    SIENNA2 = ((238, 121, 66), EXTRA)
    SIENNA3 = ((205, 104, 57), EXTRA)
    SIENNA4 = ((139, 71, 38), EXTRA)
    SKYBLUE1 = ((135, 206, 255), EXTRA)
    SKYBLUE2 = ((126, 192, 238), EXTRA)
    SKYBLUE3 = ((108, 166, 205), EXTRA)
    SKYBLUE4 = ((74, 112, 139), EXTRA)
    SLATEBLUE1 = ((131, 111, 255), EXTRA)
    SLATEBLUE2 = ((122, 103, 238), EXTRA)
    SLATEBLUE3 = ((105, 89, 205), EXTRA)
    SLATEBLUE4 = ((71, 60, 139), EXTRA)
    SLATEGRAY1 = ((198, 226, 255), EXTRA)
    SLATEGRAY2 = ((185, 211, 238), EXTRA)
    SLATEGRAY3 = ((159, 182, 205), EXTRA)
    SLATEGRAY4 = ((108, 123, 139), EXTRA)
    SNOW2 = ((238, 233, 233), EXTRA)
    SNOW3 = ((205, 201, 201), EXTRA)
    SNOW4 = ((139, 137, 137), EXTRA)
    SPRINGGREEN1 = ((0, 238, 118), EXTRA)
    SPRINGGREEN2 = ((0, 205, 102), EXTRA)
    SPRINGGREEN3 = ((0, 139, 69), EXTRA)
    STEELBLUE1 = ((99, 184, 255), EXTRA)
    STEELBLUE2 = ((92, 172, 238), EXTRA)
    STEELBLUE3 = ((79, 148, 205), EXTRA)
    STEELBLUE4 = ((54, 100, 139), EXTRA)
    TAN1 = ((255, 165, 79), EXTRA)
    TAN2 = ((238, 154, 73), EXTRA)
    TAN4 = ((139, 90, 43), EXTRA)
    THISTLE1 = ((255, 225, 255), EXTRA)
    THISTLE2 = ((238, 210, 238), EXTRA)
    THISTLE3 = ((205, 181, 205), EXTRA)
    THISTLE4 = ((139, 123, 139), EXTRA)
    TOMATO2 = ((238, 92, 66), EXTRA)
    TOMATO3 = ((205, 79, 57), EXTRA)
    TOMATO4 = ((139, 54, 38), EXTRA)
    TURQUOISE1 = ((0, 245, 255), EXTRA)
    TURQUOISE2 = ((0, 229, 238), EXTRA)
    TURQUOISE3 = ((0, 197, 205), EXTRA)
    TURQUOISE4 = ((0, 134, 139), EXTRA)
    TURQUOISEBLUE = ((0, 199, 140), EXTRA)
    VIOLETRED = ((208, 32, 144), EXTRA)
    VIOLETRED1 = ((255, 62, 150), EXTRA)
    VIOLETRED2 = ((238, 58, 140), EXTRA)
    VIOLETRED3 = ((205, 50, 120), EXTRA)
    VIOLETRED4 = ((139, 34, 82), EXTRA)
    WARMGREY = ((128, 128, 105), EXTRA)
    WHEAT1 = ((255, 231, 186), EXTRA)
    WHEAT2 = ((238, 216, 174), EXTRA)
    WHEAT3 = ((205, 186, 150), EXTRA)
    WHEAT4 = ((139, 126, 102), EXTRA)
    YELLOW2 = ((238, 238, 0), EXTRA)
    YELLOW3 = ((205, 205, 0), EXTRA)
    YELLOW4 = ((139, 139, 0), EXTRA)

    def is_standard(self) -> bool:
        """
        Whether or not this color is one of the 140 standard HTML colors.
        """
        return self.value[1]

    def brightness(self) -> int:
        """
        Returns the average of the RGB values.

        NOTE: This is different than the V brightness in HSV. V is computed as
        the highest of R, G, B, not the average,
        """
        return color_brightness(self.value[0])

    def monochrome(self, hue=0.0) -> "NamedColor":
        """
        Returns the corresponding grayscale NamedColor (determined by average
        brightness).

        :param hue: FIXME
        """
        gray = self.brightness()
        return NamedColor.by_value(gray, gray, gray)

    def lighter(self) -> "NamedColor":
        """Returns a NamedColor that is halfway between the brightness of this color and that of full white."""
        return NamedColor.by_value(color_lighter(self.value[0]))

    def darker(self) -> "NamedColor":
        """Returns a NamedColor that is half as bright."""
        return NamedColor.by_value(color_darker(self.value[0]))

    def subdued(self) -> "NamedColor":
        """
        Returns a darker/lighter version of this color that may be suitable to
        use as a background color (e.g. pink for red, light gray for dark gray,
        and vice versa).
        """
        return NamedColor.by_value(color_subdued(self.value[0]))

    def outline(self) -> "NamedColor":
        """
        Returns either black or white, depending on if this color is light or dark
        (e.g. to outline it in case the original color is hard to see).
        """
        is_dark = self.brightness() < 128
        return NamedColor.WHITE if is_dark else NamedColor.BLACK

    def hsv(self) -> tuple:
        """
        This color in terms of HSV values.

        Hue = The position on the ROYGBIV spetrum where Red is near 0.0 and
            Violet is near 1.0. NOTE: Grayscale colors (no hue at all) are
            0.0 by definition.

        Saturation = How close together the highest RGB value and the lowest
            are. For example, white, grays, black are 0.0 (fully unsaturated),
            while pure RED, GREEN, BLUE, YELLOW, CYAN, etc. are 1.0 (fully
            saturated).

        Value (Brightness) = The highest RGB value. BLACK is 0.0. Pure WHITE,
            RED, GREEN, etc. are 1.0.

        :return: A float tuple.
        """
        return rgb_to_hsv(*self.float_tuple()[:3])

    def hue_group(self) -> int:
        return -1 if self.is_gray() else hue_group(self.hsv()[0])

    def is_gray(self):
        """
        Whether or not the color is white/gray/black (i.e. the saturation is zero).
        """
        red, green, blue = self.primary_value()
        return red == green == blue

    def complementary(self, degrees=0.0) -> "NamedColor":
        """
        Finds 1 or 2 complementary colors to go with this color.

        :param degrees: How far apart on the color wheel the complimentary colors
            should be. Defaults to 0, meaning return a list with just the one
            complimentary color directly across the wheel (e.g. RED -> [GREEN],
            YELLOW -> [VIOLET]). For exact triadics (e.g. the primary colors of
            RED -> [BLUE, YELLOW]), use 120 (not 60).

        :return: A list of complimentary NamedColor(s).
        """
        return [NamedColor.by_value(color_tuple) for color_tuple in color_complementary(self.value[0], degrees)]

    def hex_format(self) -> str:
        '''Returns color in hex format'''
        return color_hex_format(self.value[0])

    def float_tuple(self, alpha=1.0) -> tuple:
        '''
        Returns a tuple in which the values range from 0.0 to 1.0, and a fourth
        argument specifies the alpha level, also 0.0-1.0.

        :param alpha: The alpha value to use (between 0.0 and 1.0). Defaults to 1.0.
        '''
        return float_tuple(self.value[0], alpha=alpha)

    def hue_name(self) -> str:
        return HUE_NAMES[-1 if self.is_gray() else hue_group(self.hsv()[0])]

    @classmethod
    def all_colors(cls, *args, only_standard=False, sort_by='unsorted') -> list:
        def key_hue_group(color):
            return (color.hue_group(), -color.brightness())

        def key_hue(color):
            return color.hsv()

        def key_brightness(color):
            return color.brightness()

        def key_name(color):
            return color.name

        if sort_by == 'unsorted':
            key_fn = None
        elif sort_by == 'hue_group':
            key_fn = key_hue_group
        elif sort_by in ['hue', 'hsv']:
            key_fn = key_hue
        elif sort_by in ['brightness', 'bright']:
            key_fn = key_brightness
        else:
            key_fn = key_name

        result = [e for e in cls if not only_standard or e.is_standard]
        if key_fn:
            result.sort(key=key_fn)
        return result

    @classmethod
    def by_value(cls, value, /, *args, only_standard=False):
        """
        Finds the closest pre-defined color that matches the given RGB tuple.

        Arguments:
            value -- either a tuple, or a string, or the Red value (the first of three-four integers).
            2nd arg -- the Green value (int).
            3rd arg -- the Blue value (int).
            4th arg -- the Alpha value (int) -- ignored.
            only_standard = Whether or not to confine the search to the standard HTML colors.

        Examples:
            NamedColor.by_value(128,128,0)
            NamedColor.by_value(128,128,0,32)
            rgb = (128,128,0); NamedColor.by_value(rgb)
            rgb = (128,128,0); NamedColor.by_value(*rgb)
            rgba = (128,128,0,32); NamedColor.by_value(rgba)
            rgba = (128,128,0,32); NamedColor.by_value(*rgba)
            NamedColor.by_value("#FFFFFF")
            NamedColor.by_value("#FFFFFF88")
            NamedColor.by_value("FFFFFF")
            NamedColor.by_value("FFFFFF88")

        """
        if value is None:
            return None
        t = type(value)
        if t is int:
            value = (value, *args)
        elif t is str:
            value = color_parse(value)
        elif t is not tuple:
            raise ValueError(f"{t} is an invalid type for the first positional argument of NamedColor.by_value()")

        best_match_so_far = None
        best_match_off_by = 99999
        for e in cls:
            off_by = color_distance(value, e.value[0])
            if off_by <= 0.001:
                # exact match!
                return e
            if off_by < best_match_off_by:
                best_match_off_by = off_by
                best_match_so_far = e
            if only_standard and (e == NamedColor.BLACK):
                break
        return best_match_so_far



# ############################################################################
#                                                        Stand-Alone Functions
# ############################################################################

def color_parse(expr: any, colormap2=None, default=None) -> tuple:
    """
    Parses the input/expression to create an RGB or an RGBA int tuple.

    :param expr: Any of these:
        * A named color (any case) from the `NamedColor` enum. This includes the140 HTML/X11 color names,
          the 7 gray/grey alternate spellings, and 400+ additional color names commonly used.
        * A named color (any case) that is defined (as lower case) in the
          optional `colormap2` dictionary -- in which case, the associated value
          is parsed instead.
        * Hex format `str` (#ff0088, #ff008840) -- the leading hash is optional.
          (Returns a 3- or 4-tuple.)
        * A `str` with an RGB tuple "(255,0,136)" or an RGBA tuple
          "(255,0,136,48)" -- the parens are optional.
          (Returns a 3- or 4-tuple.)
        * A tuple (any count) -- simply passed thru (without any checks on
          whether the tuple actually represents an RGB or RGBA color).

    :param colormap2: (Optional) A secondary dictionary of color names (the NamedColor enum being the primary map).
        expressions (e.g. the colors of
        a syntax highlight scheme by purpose). The associated value can be
        expressed in any form accepted by `expr` (but use a tuple of ints for
        efficiency). Defaults to an empty map. NOTE: The keys must be lower case.

    :param default: (Optional) The value to return when the expr cannot be resolved.
        Defaults to None.

    :return: A 3- or 4-tuple of ints (0-255), depending on the `expr`.

    See also: `PIL.ImageColor.colormap` (the 147 HTML/X11 colors).
    See also: `PIL.ImageColor.getrgb()` and `PIL.ImageColor.getcolor()`.
    See also: `reportlab` (PDF library) also has a set of color processing utilities.
    See also: `colorsys` (python build-in library) for converting between
    color system (e.g. RGB -> HSV).
    """
    if not expr:
        expr = default
    if not expr:
        return None

    if colormap2 is None:
        colormap2 = {}

    # First crack at the expr being a direct (non-string) color representation
    if not isinstance(expr, str):
        return _distilled_color_tuple(expr)

    # If the expr is a redirect, then do the substitution and try again
    expr = expr.strip().casefold()
    if colormap2 and expr in colormap2.keys():
        expr = colormap2[expr]
        # Second crack at the expr being a direct (non-string) color representation
        if not isinstance(expr, str):
            return _distilled_color_tuple(expr)
        expr = expr.strip().casefold()

    # We've exhausted all non-str possibilities

    if named_color := NamedColor.by_name(expr):
        return named_color.value[0]

    return _color_parse_hex(expr)


def _color_parse_hex(expr):
    color = None
    expr = re.sub(r"[^#0-9a-fA-F,]", "", expr)
    if m := re.match(r"#?([0-9a-fA-F]{6,8})", expr):
        b = bytes.fromhex(m[1])
        color = tuple(int(x) for x in b)
    else:
        parts = expr.split(",")
        if len(parts) >= 3:
            color = tuple(int(x) for x in parts)
    return color  # might still be None after all that


def _distilled_color_tuple(expr):
    if isinstance(expr, tuple):
        return expr
    if isinstance(expr, list):
        return tuple(expr)
    return expr.value[0] if isinstance(expr, NamedColor) else None


def is_color(possible_color_tuple) -> bool:
    """
    Analyzes `possible_color_tuple` to see if the value could properly represent
    a color. Namely it is a 3-tuple or a 4-tuple (or list), and all of those 3-4
    elements are either ints (0-255) ir all floats (0.0 to 1.0).

    :param possible_color_tuple: the candidate value.
    :return: True if it looks like a color tuple.
    """
    if not (isinstance(possible_color_tuple, (tuple, list))):
        return False
    count = len(possible_color_tuple)
    if count < 3 or count > 4:
        return False
    float_count = 0
    above_1_count = 0

    for v in possible_color_tuple:
        if v < 0 or v > 255:
            return False
        if isinstance(v, float):
            float_count += 1
        if v > 1:
            above_1_count += 1
    return above_1_count == 0 or float_count == 0


def is_float_tuple(color_tuple) -> bool:
    """
    Analyzes a color tuple to see if it is a Kivy style with
    floats (0.0 to 1.0), or a traditional style with ints (0-255).
    NOTE: For a few edge cases (where all elements are exactly 0 or exactly 1)
    tie goes to True (is floats). For all 0's, it's the same either way.
    All 0's and 1's is rare for an int tuple but quite common for a float tuple
    (WHITE, RED, GREEN, BLUE, CYAN, ...).

    :param color_tuple: Either a 3- or 4-tuple.
    :return: True if it is Kivy style.
    """
    return not any(value > 1.0 or value < 0.0 for value in color_tuple)


def float_hue(hue):
    '''
    Converts a hue from an integer (-1 - 360) to a float (0.0 to 1.0).
    Or, if it is already a float, just passes it on.
    '''
    if isinstance(hue, float) and hue < 1.0:
        return hue
    return max(0.0, min(hue / 360, 1.0))


def float_color(int_color):
    '''
    Converts an RGB value from integer (0-255) to float (0.0 to 1.0).
    '''
    return min(int_color / 255, 1.0) if int_color is not None else None


def float_tuple(color_tuple, alpha=None) -> tuple:
    '''
    Converts an RGB tuple from integers (0-255) to floats (0.0 to 1.0).

    :param int_tuple: Either a 3-tuple or a 4-tuple of integers (0-255)
    :param alpha: The alpha value to use (between 0.0 and 1.0).
        Defaults to `None`. In the case of a 4-tuple, `None` means the alpha
        value will be converted to float along with the RGB. In the case
        of a 3-tuple, `None` means it will remain a 3-tuple.

    :return: A corresponding tuple of floats.
    '''
    if not color_tuple:
        return None
    if is_float_tuple(color_tuple):
        return (*color_tuple[:3], alpha) if alpha else color_tuple
    if len(color_tuple) == 3:
        red, green, blue = color_tuple
        old_alpha = None
    elif len(color_tuple) == 4:
        red, green, blue, old_alpha = color_tuple
    else:
        raise ValueError(f"float_tuple() requires a 3-tuple or a 4-tuple, but a {len(color_tuple)}-tuple was given.")
    if not alpha:
        alpha = float_color(old_alpha)

    if alpha is not None:
        return (float_color(red), float_color(green), float_color(blue), alpha)
    return (float_color(red), float_color(green), float_color(blue))


def int_color(float_color):
    '''
    Converts an RGB value from float (0.0 to 1.0) to integer (0 to 255).
    '''
    return min(int(float_color * 255), 255) if float_color is not None else None


def int_tuple(float_tuple, alpha=None) -> tuple:
    '''
    Converts an RGB tuple from floats (0.0 to 1.0) to integers (0 to 255).

    :param int_tuple: Either a 3-tuple or a 4-tuple of floats (0.0 to 0.1)
    :param alpha: The alpha value to use (between 0 and 255).
        Defaults to `None`. In the case of a 4-tuple, `None` means the alpha
        value will be converted to int along with the RGB. In the case
        of a 3-tuple, `None` means it will remain a 3-tuple.

    :return: A corresponding tuple of ints.
    '''
    if not float_tuple:
        return None
    if len(float_tuple) == 3:
        red, green, blue = float_tuple
        old_alpha = None
    elif len(float_tuple) == 4:
        red, green, blue, old_alpha = float_tuple
    else:
        raise ValueError(f"int_tuple() requires a 3-tuple or a 4-tuple, but a {len(int_tuple)}-tuple was given.")
    if not alpha:
        alpha = int_color(old_alpha)

    if alpha is not None:
        return (int_color(red), int_color(green), int_color(blue), int_color(alpha))
    return (int_color(red), int_color(green), int_color(blue))


def color_brightness(int_tuple) -> int:
    """
    :param int_tuple: Either a 3- or 4-tuple of integers (0-255).
    (The alpha channel is ignored.)

    :return: The average of the RGB values.
    """
    return int((sum(int_tuple[:3])) / 3)


def color_monochrome(int_tuple, hue=-1) -> tuple:
    """
    :param int_tuple: Either a 3- or 4-tuple of integers (0-255).
    (The alpha channel is ignored.)

    :return: A 3-tuple of RGB ints for the corresponding monochrome color
    (determined by average brightness).
    """
    # FIXME hue
    h, s, v = rgb_to_hsv(float_tuple(int_tuple))

    return hsv_to_rgb(float_hue(hue), s, v)


def color_lighter(int_tuple) -> tuple:
    """
    :param int_tuple: Either a 3- or 4-tuple of integers (0-255).
    (The alpha channel is ignored.)

    :return: A 3-tuple that is halfway between the brightness of
    this color and that of full white.
    """
    red, green, blue = int_tuple[:3]
    red = int(red + (255 - red) / 2)
    green = int(green + (255 - green) / 2)
    blue = int(blue + (255 - blue) / 2)
    return (red, green, blue)


def color_darker(int_tuple) -> tuple:
    """
    :param int_tuple: Either a 3- or 4-tuple of integers (0-255).
    (The alpha channel is ignored.)

    :return: A 3-tuple that is half as bright.
    """
    red, green, blue = int_tuple[:3]
    red = int(red / 2)
    green = int(green / 2)
    blue = int(blue / 2)
    return (red, green, blue)


def color_subdued(color_tuple) -> tuple:
    """
    Returns a darker/lighter version of this color that may be suitable to use as a
    background color (e.g. pink for red, light gray for dark gray, and vice versa).

        :param color_tuple: Can be either Kivy style with floats (0.0 to 1.0),
    or a traditional style with ints (0-255), with optional alpha channel,
    i.e. 3 or 4 elements.

    :return: A 3-tuple of the corresponding type (floats or ints)
    """
    if was_float := is_float_tuple(color_tuple):
        color_tuple = int_tuple(color_tuple)
    is_dark = color_brightness(color_tuple) < 128
    result = color_lighter(color_tuple) if is_dark else color_darker(color_tuple)
    return float_tuple(result) if was_float else result


def color_outline(color_tuple) -> tuple:
    """
    Returns either black or white, depending on if this color is light or dark
    (e.g. to outline it in case the original color is hard to see).

    :param color_tuple: Can be either Kivy style with floats (0.0 to 1.0),
    or a traditional style with ints (0-255), with optional alpha channel,
    i.e. 3 or 4 elements.

    :return: A 3-tuple of the corresponding type (floats or ints)
    """
    if was_float := is_float_tuple(color_tuple):
        color_tuple = int_tuple(color_tuple)
    is_dark = color_brightness(color_tuple) < 128
    result = (255, 255, 255) if is_dark else (0, 0, 0)
    return float_tuple(result) if was_float else result


def color_complementary(color_tuple, degrees=0.0) -> List[tuple]:
    """
    Determines complimentary color(s) for the given RGB color tuple.

    :param color_tuple: A 3-tuple or 4-tuple of RGB values (alpha is ignored).
        They can be ints (0-255) or floats (0.0-1.0).

    :param degrees: How far apart on the color wheel the complimentary colors
        should be. Defaults to 0, meaning return a list with just the one
        complimentary color directly across the wheel (e.g. RED -> [GREEN],
        YELLOW -> [VIOLET]). For exact triadics (e.g. the primary colors of
        RED -> [BLUE, YELLOW]), use 120 (not 60).

    :return: A list of 3-tuples in the original type (ints or floats).
    """
    if was_int := not is_float_tuple(color_tuple):
        color_tuple = float_tuple(color_tuple)
    h, s, v = rgb_to_hsv(color_tuple[:3])
    float_distance = degrees / 720.0
    comp_hue = [(h + 0.5 - float_distance) % 1.0]
    result = [hsv_to_rgb((comp_hue, s, v))]
    if degrees > 0.0:
        comp_hue = [(h + 0.5 + float_distance) % 1.0]
        result.append(hsv_to_rgb((comp_hue, s, v)))
    if was_int:
        result = [int_tuple(color_tuple) for color_tuple in result]
    return result


def color_hex_format(color_tuple) -> str:
    """
    Returns the color in hex format.

    :param color_tuple: Can be either Kivy style with floats (0.0 to 1.0),
    or a traditional style with ints (0-255), with optional alpha channel,
    i.e. 3 or 4 elements.

    :return: A 6- or 8-digit hex string with a "#" prefix.
    """
    if is_float_tuple(color_tuple):
        color_tuple = int_tuple(color_tuple)
    if len(color_tuple) == 3:
        return '#{:02X}{:02X}{:02X}'.format(*color_tuple)
    elif len(color_tuple) == 4:
        return '#{:02X}{:02X}{:02X}{:02X}'.format(*color_tuple)
    return ''


def color_distance(int_tuple1, int_tuple2) -> float:
    """
    Determines how similar two colors are, i.e. the distance between them
    in r,g,b, space.

    :return: A float between 0 and 443.4050 where zero is an exact match
    and 443.4050 is the distance between Black and White.

    Credit: Inspired by reportlab.lib.colors.
    """
    red1, green1, blue1 = int_tuple1[:3]
    red2, green2, blue2 = int_tuple2[:3]
    if (red1 == red2) and (green1 == green2) and (blue1 == blue2):
        return 0.0  # avoid math rounding issues
    return math.sqrt((red1 - red2)**2 + (green1 - green2)**2 + (blue1 - blue2)**2)


def as_color(input: any) -> tuple:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    RGB tuples. Either a 3-tuple or a 4-tuple will be returned, depending on
    the input.

    A color (as configured) can be represented in hex format e.g. #ff0088 or
    #ff008840, or a tuple e.g. (255,0,136) or (255,0,136,40), or the color
    name (e.g. SKYBLUE4) accordibng to our `NamedColor` enum (550 enumerated
    colors). The leading number-sign (#) is optional for hex format. Parens
    are optional for RGB tuples. All settings are case-insensitive.

    NOTE: The only difference between `as_color` as `as_named_color` is what
    type of value is returned. Both accept the same variety of inputs.
    """
    return color_parse(input)


def as_named_color(input: any) -> NamedColor:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    our `NamedColor` enum (i.e. one of 550 enumerated colors). Be aware, if
    the input includes an alpha channel (a fourth value), it will be ignored
    when converted to a NamedColor.

    A color (as configured) can be represented in hex format e.g. #ff0088 or
    #ff008840, or a tuple e.g. (255,0,136) or (255,0,136,40), or the color
    name (e.g. SKYBLUE4) accordibng to our `NamedColor` enum (550 enumerated
    colors). The leading number-sign (#) is optional for hex format. Parens
    are optional for RGB tuples. All settings are case-insensitive.

    NOTE: The only difference between `as_color` as `as_named_color` is what
    type of value is returned. Both accept the same variety of inputs.
    """
    return NamedColor.by_value(color_parse(input))


def hue_group(hue) -> int:
    """
    Rounds off the given hue to one of 12 groups.

    :param hue: The hue to convert, either expressed as int degrees
        (-1 thru 360) or a float (0.0 - 0.9999)

    :return: The hue group in int degrees: 30, 60, 90, ... 330, or -1 if grayscale
    """
    # Leave grayscale indicator alone
    if hue < 0:
        return -1

    # convert float (0.0-1.0) to int (0-359)
    if isinstance(hue, float) and hue < 1.0:
        hue = round(hue * 12.0) * 30

    hue = int(hue)
    return 0 if hue > 330 else hue
