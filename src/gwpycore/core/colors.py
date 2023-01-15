from enum import Enum, unique
from typing import Tuple
import re
import math

from ..core.exceptions import GWValueError


__all__ = [
    'NamedColor',
    'color_parse',
    'float_tuple',
    'color_brightness',
    'color_subdued',
    'color_darker',
    'color_gray_version',
    'color_hex_format',
    'color_lighter',
    'color_outline',
    'color_distance',
    'as_color',
    'as_named_color',
]


# ############################################################################
#                                                            NamedColor (enum)
# ############################################################################

@unique
class NamedColor(Enum):
    """
    An enumeration of 550+ specific colors (including the 140 standard HTML
    colors names) as RGB tuples(0..256, 0..256,0..256), but also available
    as float tuples with an alpha factor (0.0..1.0,0.0..1.0, 0.0..1.0, 0.0..1.0).

    See also: ReportLab has its own set of 150 color constants
    (reportlab.lib.colors), along with numerous functions for converting colors
    (e.g. from RGB to CMYK).

    NamedColor.AZURE.hex_format() == #F0FFFF
    NamedColor.AZURE.float_tuple() == (0.0,0.0,0.0,1.0)
    NamedColor.AZURE.float_tuple(alpha=0.5) == (0.0,0.0,0.0,0.5)
    NamedColor.by_name("azure") == NamedColor.AZURE
    NamedColor.by_name("nosuch") == None
    NamedColor.by_value("#F0FFFF") == NamedColor.AZURE # exact match
    NamedColor.by_value("F0FFFF") == NamedColor.AZURE # exact match
    NamedColor.by_value((240, 255, 255)) == NamedColor.AZURE1 # exact match
    NamedColor.by_value((241, 254, 250)) == NamedColor.AZURE1 # (being the closest match)
    """

    # REDS

    RED = (255, 0, 0)  # #FF0000
    DARKRED = (139, 0, 0)  # #8B0000
    CRIMSON = (220, 20, 60)  # #DC143C
    INDIANRED = (205, 92, 92)  # #CD5C5C
    LIGHTCORAL = (240, 128, 128)  # #F08080
    SALMON = (250, 128, 114)  # #FA8072
    LIGHTSALMON = (255, 160, 122)  # #FFA07A
    DARKSALMON = (233, 150, 122)  # #E9967A
    FIREBRICK = (178, 34, 34)  # #B22222

    # PINKS

    PINK = (255, 192, 203)  # #FFC0CB
    LIGHTPINK = (255, 182, 193)  # #FFB6C1
    HOTPINK = (255, 105, 180)  # #FF69B4
    DEEPPINK = (255, 20, 147)  # #FF1493
    MEDIUMVIOLETRED = (199, 21, 133)  # #C71585
    PALEVIOLETRED = (219, 112, 147)  # #DB7093

    # ORANGES

    ORANGE = (255, 165, 0)  # #FFA500
    DARKORANGE = (255, 140, 0)  # #FF8C00
    CORAL = (255, 127, 80)  # #FF7F50
    TOMATO = (255, 99, 71)  # #FF6347
    ORANGERED = (255, 69, 0)  # #FF4500

    # YELLOWS

    YELLOW = (255, 255, 0)  # #FFFF00
    LIGHTYELLOW = (255, 255, 224)  # #FFFFE0
    GOLD = (255, 215, 0)  # #FFD700
    LEMONCHIFFON = (255, 250, 205)  # #FFFACD
    LIGHTGOLDENRODYELLOW = (250, 250, 210)  # #FAFAD2
    PAPAYAWHIP = (255, 239, 213)  # #FFEFD5
    MOCCASIN = (255, 228, 181)  # #FFE4B5
    PEACHPUFF = (255, 218, 185)  # #FFDAB9
    PALEGOLDENROD = (238, 232, 170)  # #EEE8AA
    KHAKI = (240, 230, 140)  # #F0E68C
    DARKKHAKI = (189, 183, 107)  # #BDB76B

    # PURPLES

    PURPLE = (128, 0, 128)  # #800080
    VIOLET = (238, 130, 238)  # #EE82EE
    DARKVIOLET = (148, 0, 211)  # #9400D3
    BLUEVIOLET = (138, 43, 226)  # #8A2BE2
    FUCHSIA = (255, 0, 254)  # nominally #FF00FF
    LAVENDER = (230, 230, 250)  # #E6E6FA
    THISTLE = (216, 191, 216)  # #D8BFD8
    PLUM = (221, 160, 221)  # #DDA0DD
    ORCHID = (218, 112, 214)  # #DA70D6
    MAGENTA = (255, 0, 255)  # #FF00FF
    MEDIUMORCHID = (186, 85, 211)  # #BA55D3
    MEDIUMPURPLE = (147, 112, 219)  # #9370DB
    REBECCAPURPLE = (102, 51, 153)  # #663399
    DARKORCHID = (153, 50, 204)  # #9932CC
    DARKMAGENTA = (139, 0, 139)  # #8B008B
    INDIGO = (75, 0, 130)  # #4B0082

    # GREENS

    GREENYELLOW = (173, 255, 47)  # #ADFF2F
    CHARTREUSE = (127, 255, 0)  # #7FFF00
    LAWNGREEN = (124, 252, 0)  # #7CFC00
    LIME = (0, 255, 0)  # #00FF00
    LIMEGREEN = (50, 205, 50)  # #32CD32
    PALEGREEN = (152, 251, 152)  # #98FB98
    LIGHTGREEN = (144, 238, 144)  # #90EE90
    MEDIUMSPRINGGREEN = (0, 250, 154)  # #00FA9A
    SPRINGGREEN = (0, 255, 127)  # #00FF7F
    MEDIUMSEAGREEN = (60, 179, 113)  # #3CB371
    SEAGREEN = (46, 139, 87)  # #2E8B57
    FORESTGREEN = (34, 139, 34)  # #228B22
    GREEN = (0, 128, 0)  # #008000
    DARKGREEN = (0, 100, 0)  # #006400
    YELLOWGREEN = (154, 205, 50)  # #9ACD32
    OLIVEDRAB = (107, 142, 35)  # #6B8E23
    OLIVE = (128, 128, 0)  # #808000
    DARKOLIVEGREEN = (85, 107, 47)  # #556B2F
    MEDIUMAQUAMARINE = (102, 205, 170)  # #66CDAA
    DARKSEAGREEN = (143, 188, 139)  # #8FBC8B
    LIGHTSEAGREEN = (32, 178, 170)  # #20B2AA
    DARKCYAN = (0, 139, 139)  # #008B8B
    TEAL = (0, 128, 128)  # #008080

    # BLUES

    BLUE = (0, 0, 255)  # #0000FF
    MEDIUMBLUE = (0, 0, 205)  # #0000CD
    DARKBLUE = (0, 0, 139)  # #00008B
    NAVY = (0, 0, 128)  # #000080
    CYAN = (0, 255, 255)  # #00FFFF
    LIGHTCYAN = (224, 255, 255)  # #E0FFFF
    AQUA = (0, 255, 254)  # nominally #00FFFF
    SLATEBLUE = (106, 90, 205)  # #6A5ACD
    DARKSLATEBLUE = (72, 61, 139)  # #483D8B
    MEDIUMSLATEBLUE = (123, 104, 238)  # #7B68EE
    PALETURQUOISE = (175, 238, 238)  # #AFEEEE
    AQUAMARINE = (127, 255, 212)  # #7FFFD4
    TURQUOISE = (64, 224, 208)  # #40E0D0
    MEDIUMTURQUOISE = (72, 209, 204)  # #48D1CC
    DARKTURQUOISE = (0, 206, 209)  # #00CED1
    CADETBLUE = (95, 158, 160)  # #5F9EA0
    STEELBLUE = (70, 130, 180)  # #4682B4
    LIGHTSTEELBLUE = (176, 196, 222)  # #B0C4DE
    POWDERBLUE = (176, 224, 230)  # #B0E0E6
    LIGHTBLUE = (173, 216, 230)  # #ADD8E6
    SKYBLUE = (135, 206, 235)  # #87CEEB
    LIGHTSKYBLUE = (135, 206, 250)  # #87CEFA
    DEEPSKYBLUE = (0, 191, 255)  # #00BFFF
    DODGERBLUE = (30, 144, 255)  # #1E90FF
    CORNFLOWERBLUE = (100, 149, 237)  # #6495ED
    ROYALBLUE = (65, 105, 225)  # #4169E1
    MIDNIGHTBLUE = (25, 25, 112)  # #191970

    # BROWNS

    CORNSILK = (255, 248, 220)  # #FFF8DC
    BLANCHEDALMOND = (255, 235, 205)  # #FFEBCD
    BISQUE = (255, 228, 196)  # #FFE4C4
    NAVAJOWHITE = (255, 222, 173)  # #FFDEAD
    WHEAT = (245, 222, 179)  # #F5DEB3
    BURLYWOOD = (222, 184, 135)  # #DEB887
    TAN = (210, 180, 140)  # #D2B48C
    ROSYBROWN = (188, 143, 143)  # #BC8F8F
    SANDYBROWN = (244, 164, 96)  # #F4A460
    GOLDENROD = (218, 165, 32)  # #DAA520
    DARKGOLDENROD = (184, 134, 11)  # #B8860B
    PERU = (205, 133, 63)  # #CD853F
    CHOCOLATE = (210, 105, 30)  # #D2691E
    SADDLEBROWN = (139, 69, 19)  # #8B4513
    SIENNA = (160, 82, 45)  # #A0522D
    BROWN = (165, 42, 42)  # #A52A2A
    MAROON = (128, 0, 0)  # #800000

    # WHITES

    WHITE = (255, 255, 255)  # #FFFFFF
    SNOW = (255, 250, 250)  # #FFFAFA
    HONEYDEW = (240, 255, 240)  # #F0FFF0
    MINTCREAM = (245, 255, 250)  # #F5FFFA
    AZURE = (240, 255, 255)  # #F0FFFF
    ALICEBLUE = (240, 248, 255)  # #F0F8FF
    GHOSTWHITE = (248, 248, 255)  # #F8F8FF
    WHITESMOKE = (245, 245, 245)  # #F5F5F5
    SEASHELL = (255, 245, 238)  # #FFF5EE
    BEIGE = (245, 245, 220)  # #F5F5DC
    OLDLACE = (253, 245, 230)  # #FDF5E6
    FLORALWHITE = (255, 250, 240)  # #FFFAF0
    IVORY = (255, 255, 240)  # #FFFFF0
    ANTIQUEWHITE = (250, 235, 215)  # #FAEBD7
    LINEN = (250, 240, 230)  # #FAF0E6
    LAVENDERBLUSH = (255, 240, 245)  # #FFF0F5
    MISTYROSE = (255, 228, 225)  # #FFE4E1

    # GRAYS

    GAINSBORO = (220, 220, 220)  # #DCDCDC
    LIGHTGRAY = (211, 211, 211)  # #D3D3D3
    SILVER = (192, 192, 192)  # #C0C0C0
    DARKGRAY = (169, 169, 169)  # #A9A9A9
    GRAY = (128, 128, 128)  # #808080
    DIMGRAY = (105, 105, 105)  # #696969
    LIGHTSLATEGRAY = (119, 136, 153)  # #778899
    SLATEGRAY = (112, 128, 144)  # #708090
    DARKSLATEGRAY = (47, 79, 79)  # #2F4F4F
    BLACK = (0, 0, 0)  # #000000
    # IMPORTANT -- BLACK marks the end of the standard HTML colors.

    # 448 Additional (Non-Standard) Color Names

    AQUAMARINE2 = (118, 238, 198)
    AQUAMARINE4 = (69, 139, 116)
    ANTIQUEWHITE1 = (255, 239, 219)
    ANTIQUEWHITE2 = (238, 223, 204)
    ANTIQUEWHITE3 = (205, 192, 176)
    ANTIQUEWHITE4 = (139, 131, 120)
    AZURE2 = (224, 238, 238)
    AZURE3 = (193, 205, 205)
    AZURE4 = (131, 139, 139)
    BANANA = (227, 207, 87)
    BISQUE2 = (238, 213, 183)
    BISQUE3 = (205, 183, 158)
    BISQUE4 = (139, 125, 107)
    BLUE2 = (0, 0, 238)
    BRICK = (156, 102, 31)
    BROWN1 = (255, 64, 64)
    BROWN2 = (238, 59, 59)
    BROWN3 = (205, 51, 51)
    BROWN4 = (139, 35, 35)
    BURLYWOOD1 = (255, 211, 155)
    BURLYWOOD2 = (238, 197, 145)
    BURLYWOOD3 = (205, 170, 125)
    BURLYWOOD4 = (139, 115, 85)
    BURNTSIENNA = (138, 54, 15)
    BURNTUMBER = (138, 51, 36)
    CADETBLUE1 = (152, 245, 255)
    CADETBLUE2 = (142, 229, 238)
    CADETBLUE3 = (122, 197, 205)
    CADETBLUE4 = (83, 134, 139)
    CADMIUMORANGE = (255, 97, 3)
    CADMIUMYELLOW = (255, 153, 18)
    CARROT = (237, 145, 33)
    CHARTREUSE2 = (118, 238, 0)
    CHARTREUSE3 = (102, 205, 0)
    CHARTREUSE4 = (69, 139, 0)
    CHOCOLATE1 = (255, 127, 36)
    CHOCOLATE2 = (238, 118, 33)
    CHOCOLATE3 = (205, 102, 29)
    COBALT = (61, 89, 171)
    COBALTGREEN = (61, 145, 64)
    COLDGREY = (128, 138, 135)
    CORAL1 = (255, 114, 86)
    CORAL2 = (238, 106, 80)
    CORAL3 = (205, 91, 69)
    CORAL4 = (139, 62, 47)
    CORNSILK2 = (238, 232, 205)
    CORNSILK3 = (205, 200, 177)
    CORNSILK4 = (139, 136, 120)
    CYAN2 = (0, 238, 238)
    CYAN3 = (0, 205, 205)
    DARKGOLDENROD1 = (255, 185, 15)
    DARKGOLDENROD2 = (238, 173, 14)
    DARKGOLDENROD3 = (205, 149, 12)
    DARKGOLDENROD4 = (139, 101, 8)
    DARKOLIVEGREEN1 = (202, 255, 112)
    DARKOLIVEGREEN2 = (188, 238, 104)
    DARKOLIVEGREEN3 = (162, 205, 90)
    DARKOLIVEGREEN4 = (110, 139, 61)
    DARKORANGE1 = (255, 127, 0)
    DARKORANGE2 = (238, 118, 0)
    DARKORANGE3 = (205, 102, 0)
    DARKORANGE4 = (139, 69, 0)
    DARKORCHID1 = (191, 62, 255)
    DARKORCHID2 = (178, 58, 238)
    DARKORCHID3 = (154, 50, 205)
    DARKORCHID4 = (104, 34, 139)
    DARKSEAGREEN1 = (193, 255, 193)
    DARKSEAGREEN2 = (180, 238, 180)
    DARKSEAGREEN3 = (155, 205, 155)
    DARKSEAGREEN4 = (105, 139, 105)
    DARKSLATEGRAY1 = (151, 255, 255)
    DARKSLATEGRAY2 = (141, 238, 238)
    DARKSLATEGRAY3 = (121, 205, 205)
    DARKSLATEGRAY4 = (82, 139, 139)
    DEEPPINK2 = (238, 18, 137)
    DEEPPINK3 = (205, 16, 118)
    DEEPPINK4 = (139, 10, 80)
    DEEPSKYBLUE2 = (0, 178, 238)
    DEEPSKYBLUE3 = (0, 154, 205)
    DEEPSKYBLUE4 = (0, 104, 139)
    DODGERBLUE2 = (28, 134, 238)
    DODGERBLUE3 = (24, 116, 205)
    DODGERBLUE4 = (16, 78, 139)
    EGGSHELL = (252, 230, 201)
    EMERALDGREEN = (0, 201, 87)
    FIREBRICK1 = (255, 48, 48)
    FIREBRICK2 = (238, 44, 44)
    FIREBRICK3 = (205, 38, 38)
    FIREBRICK4 = (139, 26, 26)
    FLESH = (255, 125, 64)
    GOLD2 = (238, 201, 0)
    GOLD3 = (205, 173, 0)
    GOLD4 = (139, 117, 0)
    GOLDENROD1 = (255, 193, 37)
    GOLDENROD2 = (238, 180, 34)
    GOLDENROD3 = (205, 155, 29)
    GOLDENROD4 = (139, 105, 20)
    GRAY1 = (3, 3, 3)
    GRAY2 = (5, 5, 5)
    GRAY3 = (8, 8, 8)
    GRAY4 = (10, 10, 10)
    GRAY5 = (13, 13, 13)
    GRAY6 = (15, 15, 15)
    GRAY7 = (18, 18, 18)
    GRAY8 = (20, 20, 20)
    GRAY9 = (23, 23, 23)
    GRAY10 = (26, 26, 26)
    GRAY11 = (28, 28, 28)
    GRAY12 = (31, 31, 31)
    GRAY13 = (33, 33, 33)
    GRAY14 = (36, 36, 36)
    GRAY15 = (38, 38, 38)
    GRAY16 = (41, 41, 41)
    GRAY17 = (43, 43, 43)
    GRAY18 = (46, 46, 46)
    GRAY19 = (48, 48, 48)
    GRAY20 = (51, 51, 51)
    GRAY21 = (54, 54, 54)
    GRAY22 = (56, 56, 56)
    GRAY23 = (59, 59, 59)
    GRAY24 = (61, 61, 61)
    GRAY25 = (64, 64, 64)
    GRAY26 = (66, 66, 66)
    GRAY27 = (69, 69, 69)
    GRAY28 = (71, 71, 71)
    GRAY29 = (74, 74, 74)
    GRAY30 = (77, 77, 77)
    GRAY31 = (79, 79, 79)
    GRAY32 = (82, 82, 82)
    GRAY33 = (84, 84, 84)
    GRAY34 = (87, 87, 87)
    GRAY35 = (89, 89, 89)
    GRAY36 = (92, 92, 92)
    GRAY37 = (94, 94, 94)
    GRAY38 = (97, 97, 97)
    GRAY39 = (99, 99, 99)
    GRAY40 = (102, 102, 102)
    GRAY42 = (107, 107, 107)
    GRAY43 = (110, 110, 110)
    GRAY44 = (112, 112, 112)
    GRAY45 = (115, 115, 115)
    GRAY46 = (117, 117, 117)
    GRAY47 = (120, 120, 120)
    GRAY48 = (122, 122, 122)
    GRAY49 = (125, 125, 125)
    GRAY50 = (127, 127, 127)
    GRAY51 = (130, 130, 130)
    GRAY52 = (133, 133, 133)
    GRAY53 = (135, 135, 135)
    GRAY54 = (138, 138, 138)
    GRAY55 = (140, 140, 140)
    GRAY56 = (143, 143, 143)
    GRAY57 = (145, 145, 145)
    GRAY58 = (148, 148, 148)
    GRAY59 = (150, 150, 150)
    GRAY60 = (153, 153, 153)
    GRAY61 = (156, 156, 156)
    GRAY62 = (158, 158, 158)
    GRAY63 = (161, 161, 161)
    GRAY64 = (163, 163, 163)
    GRAY65 = (166, 166, 166)
    GRAY66 = (168, 168, 168)
    GRAY67 = (171, 171, 171)
    GRAY68 = (173, 173, 173)
    GRAY69 = (176, 176, 176)
    GRAY70 = (179, 179, 179)
    GRAY71 = (181, 181, 181)
    GRAY72 = (184, 184, 184)
    GRAY73 = (186, 186, 186)
    GRAY74 = (189, 189, 189)
    GRAY75 = (191, 191, 191)
    GRAY76 = (194, 194, 194)
    GRAY77 = (196, 196, 196)
    GRAY78 = (199, 199, 199)
    GRAY79 = (201, 201, 201)
    GRAY80 = (204, 204, 204)
    GRAY81 = (207, 207, 207)
    GRAY82 = (209, 209, 209)
    GRAY83 = (212, 212, 212)
    GRAY84 = (214, 214, 214)
    GRAY85 = (217, 217, 217)
    GRAY86 = (219, 219, 219)
    GRAY87 = (222, 222, 222)
    GRAY88 = (224, 224, 224)
    GRAY89 = (227, 227, 227)
    GRAY90 = (229, 229, 229)
    GRAY91 = (232, 232, 232)
    GRAY92 = (235, 235, 235)
    GRAY93 = (237, 237, 237)
    GRAY94 = (240, 240, 240)
    GRAY95 = (242, 242, 242)
    GRAY97 = (247, 247, 247)
    GRAY98 = (250, 250, 250)
    GRAY99 = (252, 252, 252)
    GREEN2 = (0, 238, 0)
    GREEN3 = (0, 205, 0)
    GREEN4 = (0, 139, 0)
    HONEYDEW2 = (224, 238, 224)
    HONEYDEW3 = (193, 205, 193)
    HONEYDEW4 = (131, 139, 131)
    HOTPINK1 = (255, 110, 180)
    HOTPINK2 = (238, 106, 167)
    HOTPINK3 = (205, 96, 144)
    HOTPINK4 = (139, 58, 98)
    INDIANRED1 = (255, 106, 106)
    INDIANRED2 = (238, 99, 99)
    INDIANRED3 = (205, 85, 85)
    INDIANRED4 = (139, 58, 58)
    IVORY2 = (238, 238, 224)
    IVORY3 = (205, 205, 193)
    IVORY4 = (139, 139, 131)
    IVORYBLACK = (41, 36, 33)
    KHAKI1 = (255, 246, 143)
    KHAKI2 = (238, 230, 133)
    KHAKI3 = (205, 198, 115)
    KHAKI4 = (139, 134, 78)
    LAVENDERBLUSH2 = (238, 224, 229)
    LAVENDERBLUSH3 = (205, 193, 197)
    LAVENDERBLUSH4 = (139, 131, 134)
    LEMONCHIFFON2 = (238, 233, 191)
    LEMONCHIFFON3 = (205, 201, 165)
    LEMONCHIFFON4 = (139, 137, 112)
    LIGHTBLUE1 = (191, 239, 255)
    LIGHTBLUE2 = (178, 223, 238)
    LIGHTBLUE3 = (154, 192, 205)
    LIGHTBLUE4 = (104, 131, 139)
    LIGHTCYAN2 = (209, 238, 238)
    LIGHTCYAN3 = (180, 205, 205)
    LIGHTCYAN4 = (122, 139, 139)
    LIGHTGOLDENROD1 = (255, 236, 139)
    LIGHTGOLDENROD2 = (238, 220, 130)
    LIGHTGOLDENROD3 = (205, 190, 112)
    LIGHTGOLDENROD4 = (139, 129, 76)
    LIGHTPINK1 = (255, 174, 185)
    LIGHTPINK2 = (238, 162, 173)
    LIGHTPINK3 = (205, 140, 149)
    LIGHTPINK4 = (139, 95, 101)
    LIGHTSALMON2 = (238, 149, 114)
    LIGHTSALMON3 = (205, 129, 98)
    LIGHTSALMON4 = (139, 87, 66)
    LIGHTSKYBLUE1 = (176, 226, 255)
    LIGHTSKYBLUE2 = (164, 211, 238)
    LIGHTSKYBLUE3 = (141, 182, 205)
    LIGHTSKYBLUE4 = (96, 123, 139)
    LIGHTSLATEBLUE = (132, 112, 255)
    LIGHTSTEELBLUE1 = (202, 225, 255)
    LIGHTSTEELBLUE2 = (188, 210, 238)
    LIGHTSTEELBLUE3 = (162, 181, 205)
    LIGHTSTEELBLUE4 = (110, 123, 139)
    LIGHTYELLOW2 = (238, 238, 209)
    LIGHTYELLOW3 = (205, 205, 180)
    LIGHTYELLOW4 = (139, 139, 122)
    MAGENTA2 = (238, 0, 238)
    MAGENTA3 = (205, 0, 205)
    MANGANESEBLUE = (3, 168, 158)
    MAROON1 = (255, 52, 179)
    MAROON2 = (238, 48, 167)
    MAROON3 = (205, 41, 144)
    MAROON4 = (139, 28, 98)
    MEDIUMORCHID1 = (224, 102, 255)
    MEDIUMORCHID2 = (209, 95, 238)
    MEDIUMORCHID3 = (180, 82, 205)
    MEDIUMORCHID4 = (122, 55, 139)
    MEDIUMPURPLE1 = (171, 130, 255)
    MEDIUMPURPLE2 = (159, 121, 238)
    MEDIUMPURPLE3 = (137, 104, 205)
    MEDIUMPURPLE4 = (93, 71, 139)
    MELON = (227, 168, 105)
    MINT = (189, 252, 201)
    MISTYROSE2 = (238, 213, 210)
    MISTYROSE3 = (205, 183, 181)
    MISTYROSE4 = (139, 125, 123)
    NAVAJOWHITE2 = (238, 207, 161)
    NAVAJOWHITE3 = (205, 179, 139)
    NAVAJOWHITE4 = (139, 121, 94)
    OLIVEDRAB1 = (192, 255, 62)
    OLIVEDRAB2 = (179, 238, 58)
    OLIVEDRAB4 = (105, 139, 34)
    ORANGE2 = (238, 154, 0)
    ORANGE3 = (205, 133, 0)
    ORANGE4 = (139, 90, 0)
    ORANGERED2 = (238, 64, 0)
    ORANGERED3 = (205, 55, 0)
    ORANGERED4 = (139, 37, 0)
    ORCHID1 = (255, 131, 250)
    ORCHID2 = (238, 122, 233)
    ORCHID3 = (205, 105, 201)
    ORCHID4 = (139, 71, 137)
    PALEGREEN1 = (154, 255, 154)
    PALEGREEN3 = (124, 205, 124)
    PALEGREEN4 = (84, 139, 84)
    PALETURQUOISE1 = (187, 255, 255)
    PALETURQUOISE2 = (174, 238, 238)
    PALETURQUOISE3 = (150, 205, 205)
    PALETURQUOISE4 = (102, 139, 139)
    PALEVIOLETRED1 = (255, 130, 171)
    PALEVIOLETRED2 = (238, 121, 159)
    PALEVIOLETRED3 = (205, 104, 137)
    PALEVIOLETRED4 = (139, 71, 93)
    PEACHPUFF2 = (238, 203, 173)
    PEACHPUFF3 = (205, 175, 149)
    PEACHPUFF4 = (139, 119, 101)
    PEACOCK = (51, 161, 201)
    PINK1 = (255, 181, 197)
    PINK2 = (238, 169, 184)
    PINK3 = (205, 145, 158)
    PINK4 = (139, 99, 108)
    PLUM1 = (255, 187, 255)
    PLUM2 = (238, 174, 238)
    PLUM3 = (205, 150, 205)
    PLUM4 = (139, 102, 139)
    PURPLE1 = (155, 48, 255)
    PURPLE2 = (145, 44, 238)
    PURPLE3 = (125, 38, 205)
    PURPLE4 = (85, 26, 139)
    RASPBERRY = (135, 38, 87)
    RAWSIENNA = (199, 97, 20)
    RED2 = (238, 0, 0)
    RED3 = (205, 0, 0)
    ROSYBROWN1 = (255, 193, 193)
    ROSYBROWN2 = (238, 180, 180)
    ROSYBROWN3 = (205, 155, 155)
    ROSYBROWN4 = (139, 105, 105)
    ROYALBLUE1 = (72, 118, 255)
    ROYALBLUE2 = (67, 110, 238)
    ROYALBLUE3 = (58, 95, 205)
    ROYALBLUE4 = (39, 64, 139)
    SALMON1 = (255, 140, 105)
    SALMON2 = (238, 130, 98)
    SALMON3 = (205, 112, 84)
    SALMON4 = (139, 76, 57)
    SAPGREEN = (48, 128, 20)
    SEAGREEN1 = (84, 255, 159)
    SEAGREEN2 = (78, 238, 148)
    SEAGREEN3 = (67, 205, 128)
    SEASHELL2 = (238, 229, 222)
    SEASHELL3 = (205, 197, 191)
    SEASHELL4 = (139, 134, 130)
    SEPIA = (94, 38, 18)
    SGIBEET = (142, 56, 142)
    SGIBRIGHTGRAY = (197, 193, 170)
    SGICHARTREUSE = (113, 198, 113)
    SGIDARKGRAY = (85, 85, 85)
    SGIGRAY12 = (30, 30, 30)
    SGIGRAY16 = (40, 40, 40)
    SGIGRAY32 = (81, 81, 81)
    SGIGRAY36 = (91, 91, 91)
    SGIGRAY52 = (132, 132, 132)
    SGIGRAY56 = (142, 142, 142)
    SGIGRAY72 = (183, 183, 183)
    SGIGRAY76 = (193, 193, 193)
    SGIGRAY92 = (234, 234, 234)
    SGIGRAY96 = (244, 244, 244)
    SGILIGHTBLUE = (125, 158, 192)
    SGILIGHTGRAY = (170, 170, 170)
    SGIOLIVEDRAB = (142, 142, 56)
    SGISALMON = (198, 113, 113)
    SGISLATEBLUE = (113, 113, 198)
    SGITEAL = (56, 142, 142)
    SIENNA1 = (255, 130, 71)
    SIENNA2 = (238, 121, 66)
    SIENNA3 = (205, 104, 57)
    SIENNA4 = (139, 71, 38)
    SKYBLUE1 = (135, 206, 255)
    SKYBLUE2 = (126, 192, 238)
    SKYBLUE3 = (108, 166, 205)
    SKYBLUE4 = (74, 112, 139)
    SLATEBLUE1 = (131, 111, 255)
    SLATEBLUE2 = (122, 103, 238)
    SLATEBLUE3 = (105, 89, 205)
    SLATEBLUE4 = (71, 60, 139)
    SLATEGRAY1 = (198, 226, 255)
    SLATEGRAY2 = (185, 211, 238)
    SLATEGRAY3 = (159, 182, 205)
    SLATEGRAY4 = (108, 123, 139)
    SNOW2 = (238, 233, 233)
    SNOW3 = (205, 201, 201)
    SNOW4 = (139, 137, 137)
    SPRINGGREEN1 = (0, 238, 118)
    SPRINGGREEN2 = (0, 205, 102)
    SPRINGGREEN3 = (0, 139, 69)
    STEELBLUE1 = (99, 184, 255)
    STEELBLUE2 = (92, 172, 238)
    STEELBLUE3 = (79, 148, 205)
    STEELBLUE4 = (54, 100, 139)
    TAN1 = (255, 165, 79)
    TAN2 = (238, 154, 73)
    TAN4 = (139, 90, 43)
    THISTLE1 = (255, 225, 255)
    THISTLE2 = (238, 210, 238)
    THISTLE3 = (205, 181, 205)
    THISTLE4 = (139, 123, 139)
    TOMATO2 = (238, 92, 66)
    TOMATO3 = (205, 79, 57)
    TOMATO4 = (139, 54, 38)
    TURQUOISE1 = (0, 245, 255)
    TURQUOISE2 = (0, 229, 238)
    TURQUOISE3 = (0, 197, 205)
    TURQUOISE4 = (0, 134, 139)
    TURQUOISEBLUE = (0, 199, 140)
    VIOLETRED = (208, 32, 144)
    VIOLETRED1 = (255, 62, 150)
    VIOLETRED2 = (238, 58, 140)
    VIOLETRED3 = (205, 50, 120)
    VIOLETRED4 = (139, 34, 82)
    WARMGREY = (128, 128, 105)
    WHEAT1 = (255, 231, 186)
    WHEAT2 = (238, 216, 174)
    WHEAT3 = (205, 186, 150)
    WHEAT4 = (139, 126, 102)
    YELLOW2 = (238, 238, 0)
    YELLOW3 = (205, 205, 0)
    YELLOW4 = (139, 139, 0)

    def is_standard(self) -> bool:
        """
        Whether or not this color is one of the 140 standard HTML colors.
        """
        for c in list(NamedColor):
            if c == self:
                return True
            if c == NamedColor.BLACK:
                return False

    def brightness(self) -> int:
        """
        Returns the average of the RGB values.
        """
        rgb = self.value
        return int(sum(rgb) / 3)

    def gray_version(self) -> "NamedColor":
        """
        Returns the corresponding grayscale NamedColor (determined by average
        brightness).
        """
        gray = self.brightness()
        return NamedColor.by_value(gray, gray, gray)

    def lighter(self) -> "NamedColor":
        """Returns a NamedColor that is halfway between the brightness of this color and that of full white."""
        return NamedColor.by_value(color_lighter(self.value))

    def darker(self) -> "NamedColor":
        """Returns a NamedColor that is half as bright."""
        return NamedColor.by_value(color_darker(self.value))

    def subdued(self) -> "NamedColor":
        """
        Returns a darker/lighter version of this color that may be suitable to
        use as a background color (e.g. pink for red, light gray for dark gray,
        and vice versa).
        """
        return NamedColor.by_value(color_subdued(self.value))

    def outline(self) -> "NamedColor":
        """
        Returns either black or white, depending on if this color is light or dark
        (e.g. to outline it in case the original color is hard to see).
        """
        is_dark = self.brightness() < 128
        return NamedColor.WHITE if is_dark else NamedColor.BLACK

    def hex_format(self) -> str:
        '''Returns color in hex format'''
        return color_hex_format(self.value)

    def float_tuple(self, alpha=256) -> Tuple:
        '''
        Returns a tuple in which the values range from 0.0 to 1.0, and a fourth
        argument specifies the alpha level, also 0.0-1.0.

        :param alpha: The alpha value to use (between 0.0 and 1.0). Defaults to 1.0.
        '''
        return float_tuple(self.value, alpha)

    @classmethod
    def by_name(cls, name: str):
        name = name.upper().strip()
        try:
            return NamedColor[name]
        except KeyError:
            return None

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
            raise GWValueError(f"{t} is an invalid type for the first positional argument of NamedColor.by_value()")

        best_match_so_far = None
        best_match_off_by = 99999
        for e in cls:
            off_by = color_distance(value, e.value)
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

def color_parse(expr: any, names=None) -> Tuple:
    """
    Parses the input/expression to create an RGB 3-tuple (or 4-tuple). The input can be:

        * A key value of the optional names dictionary (e.g. a base16 scheme)
          -- in which case, the associated value is parsed instead.
        * One of the NamedColor names. (Returns a 3-tuple.)
        * A NamedColor element. (Returns a 3-tuple.)
        * Hex format (#ff0088, #ff008840) -- the leading hash is optional. (Returns a 3- or 4-tuple.)
        * A string with an RGB tuple "(255,0,136)" -- the parens are optional. (Returns a 3- or 4-tuple.)
        * A tuple (any count) -- simply passed thru.
    """
    if names is None:
        names = {}
    if isinstance(expr, Tuple):
        return expr

    if isinstance(expr, NamedColor):
        return expr.value

    if isinstance(expr, str) and expr in names:
        expr = names[expr]

    if not isinstance(expr, str):
        return None

    color = NamedColor.by_name(expr)
    if color:
        return color.value

    expr = re.sub(r"[^#0-9a-fA-F,]", "", expr)
    if m := re.match(r"#?([0-9a-fA-F]{6,8})", expr):
        b = bytes.fromhex(m[1])
        color = tuple(int(x) for x in b)
    else:
        parts = expr.split(",")
        if len(parts) >= 3:
            color = tuple(int(x) for x in parts)

    return color


def float_tuple(int_tuple, default_alpha=255) -> Tuple:
    '''
    Converts an RGB tuple from integers (0-255) to floats (0.0 to 1.0).

    :param int_tuple: Either a 3-tuple or a 4-tuple of integers (0-255)

    :param alpha: The alpha value to use (between 0-255), in the event
    that the int_tuple is not already a 4-tuple. Defaults to 255.

    :return: A 4-tuple of floats.
    '''
    if not int_tuple:
        return None
    if len(int_tuple) == 3:
        red, green, blue = int_tuple
        alpha = default_alpha
    elif len(int_tuple) == 4:
        red, green, blue, alpha = int_tuple
    else:
        raise GWValueError(f"float_tuple() requires a 3-tuple or a 4-tuple, but a {len(int_tuple)}-tuple was given.")

    return ((red + 1) / 256, (green + 1) / 256, (blue + 1) / 256, (alpha + 1) / 256)


def color_brightness(int_tuple) -> int:
    """
    Returns the average of the RGB values.
    """
    return int(sum(int_tuple) / 3)


def color_gray_version(int_tuple) -> Tuple:
    """
    Returns the corresponding grayscale color (determined by average
    brightness).
    """
    gray = color_brightness(int_tuple)
    return (gray, gray, gray)


def color_lighter(int_tuple) -> Tuple:
    """
    Returns a color tuple that is halfway between the brightness of
    this color and that of full white.
    """
    r, g, b = int_tuple
    r = int(r + (255 - r) / 2)
    g = int(g + (255 - g) / 2)
    b = int(b + (255 - b) / 2)
    return (r, g, b)


def color_darker(int_tuple) -> Tuple:
    """
    Returns a color tuple that is half as bright.
    """
    r, g, b = int_tuple
    r = int(r / 2)
    g = int(g / 2)
    b = int(b / 2)
    return (r, g, b)


def color_subdued(int_tuple) -> Tuple:
    """
    Returns a darker/lighter version of this color that may be suitable to use as a
    background color (e.g. pink for red, light gray for dark gray, and vice versa).
    """
    is_dark = color_brightness(int_tuple) < 128
    return color_lighter(int_tuple) if is_dark else color_darker(int_tuple)


def color_outline(int_tuple) -> Tuple:
    """
    Returns either black or white, depending on if this color is light or dark
    (e.g. to outline it in case the original color is hard to see).
    """
    is_dark = color_brightness(int_tuple) < 128
    return (256, 256, 256) if is_dark else (0, 0, 0)


def color_hex_format(int_tuple) -> str:
    '''Returns color in hex format'''
    if len(int_tuple) == 3:
        return '#{:02X}{:02X}{:02X}'.format(*int_tuple)
    elif len(int_tuple) == 4:
        return '#{:02X}{:02X}{:02X}{:02X}'.format(*int_tuple)
    return ''


def color_distance(int_tuple1, int_tuple2) -> float:
    """
    Determines how similar two colors are, i.e. the distance between them
    in r,g,b, space.

    :return: A float between 0 and 443.4050 where zero is an exact match
    and 443.4050 is the distance between Black and White.

    Credit: Inspired by reportlab.lib.colors.
    """
    r1, g1, b1 = int_tuple1
    r2, g2, b2 = int_tuple2
    if (r1 == r2) and (g1 == g2) and (b1 == b2):
        return 0.0  # avoid math rounding issues
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)


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
