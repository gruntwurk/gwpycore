from gwpycore import (
    NamedColor, float_tuple, int_tuple, is_float_tuple, color_parse,
    color_brightness, color_darker, color_distance, color_outline, color_subdued
    )
import pytest

syntax_scheme = {
    'normal': (0, 0, 0, 0),  # Invisible
    'comment': (48, 48, 48),
    'bold': 'green',
    'italics': 'FFFF0080',  # Translucent yellow
    'strikeout': '#99000099',  # Translucent red
}


def test_color_parse():
    assert color_parse((255, 255, 255)) == (255, 255, 255)
    assert color_parse("(255,255,255)") == (255, 255, 255)
    assert color_parse("255,255,255") == (255, 255, 255)
    assert color_parse("255, 255, 255") == (255, 255, 255)
    assert color_parse("   (   255  , 255  , 255 )   ") == (255, 255, 255)
    assert color_parse("#FFFFFF") == (255, 255, 255)
    assert color_parse("#ffffff") == (255, 255, 255)
    assert color_parse("FFFFFF") == (255, 255, 255)
    assert color_parse((255, 255, 255, 0)) == (255, 255, 255, 0)
    assert color_parse("#FFFFFFFF") == (255, 255, 255, 255)
    assert color_parse("FFFFFFFF") == (255, 255, 255, 255)

    assert color_parse("white") == (255, 255, 255)
    assert color_parse("WHITE") == (255, 255, 255)
    assert color_parse("White") == (255, 255, 255)
    assert color_parse("RED") == (255, 0, 0)
    assert color_parse("GREEN") == (0, 128, 0)
    assert color_parse("Blue") == (0, 0, 255)
    assert color_parse("Unknown") is None

    assert color_parse('normal', syntax_scheme) == (0, 0, 0, 0)
    assert color_parse('comment', syntax_scheme) == (48, 48, 48)
    assert color_parse('bold', syntax_scheme) == (0, 128, 0)
    assert color_parse('italics', syntax_scheme) == (255, 255, 0, 128)
    assert color_parse('strikeout', syntax_scheme) == (153, 0, 0, 153)


def test_NamedColor_construction():
    assert NamedColor.by_value("#F0FFFF") == NamedColor.AZURE
    assert NamedColor.by_value("F0FFFF") == NamedColor.AZURE

    assert NamedColor.by_name("azure") == NamedColor.AZURE
    assert NamedColor.by_name("nosuch") is None

    assert NamedColor.by_value(240, 255, 255) == NamedColor.AZURE  # exact match
    assert NamedColor.by_value(241, 254, 253) == NamedColor.AZURE  # (being the closest match)
    assert NamedColor.by_value(241, 254, 253, only_standard=True) == NamedColor.AZURE  # (being the closest match)
    assert NamedColor.by_value(241, 254, 250) == NamedColor.MINTCREAM  # (being the closest match)

    rgb = (156, 102, 31)
    assert NamedColor.by_value(rgb) == NamedColor.BRICK  # exact match allowing for non-standard colors
    assert NamedColor.by_value(156, 102, 31, only_standard=True) == NamedColor.SIENNA  # closest match sticking to standard colors
    assert NamedColor.by_value(*rgb, only_standard=True) == NamedColor.SIENNA  # closest match sticking to standard colors


def test_NamedColor_methods():
    assert NamedColor.DARKSLATEGRAY.is_standard()
    assert NamedColor.BLACK.is_standard()

    assert NamedColor.AZURE.hex_format() == "#F0FFFF"

    assert NamedColor.AZURE2.float_tuple() == float_tuple((224, 238, 238), alpha=1.0)  # AZURE2 = (224, 238, 238)
    assert not NamedColor.TURQUOISEBLUE.is_standard()

    assert NamedColor.MINTCREAM.brightness() == 250
    assert NamedColor.MINTCREAM.monochrome() == NamedColor.GRAY98
    assert NamedColor.MINTCREAM.lighter() == NamedColor.GRAY99
    assert NamedColor.MINTCREAM.darker() == NamedColor.GRAY49
    assert NamedColor.MINTCREAM.subdued() == NamedColor.GRAY49
    assert NamedColor.MINTCREAM.outline() == NamedColor.BLACK

    assert NamedColor.INDIANRED4.brightness() == 85
    assert NamedColor.INDIANRED4.monochrome() == NamedColor.SGIDARKGRAY  # between GRAY33 and GRAY34, FYI
    assert NamedColor.INDIANRED4.lighter() == NamedColor.ROSYBROWN3
    assert NamedColor.INDIANRED4.darker() == NamedColor.SEPIA
    assert NamedColor.INDIANRED4.subdued() == NamedColor.ROSYBROWN3
    assert NamedColor.INDIANRED4.outline() == NamedColor.WHITE

    assert NamedColor.MIDNIGHTBLUE.brightness() == 54
    assert NamedColor.MIDNIGHTBLUE.monochrome() == NamedColor.GRAY21
    assert NamedColor.MIDNIGHTBLUE.lighter() == NamedColor.SGILIGHTBLUE
    assert NamedColor.MIDNIGHTBLUE.darker() == NamedColor.GRAY10
    assert NamedColor.MIDNIGHTBLUE.subdued() == NamedColor.SGILIGHTBLUE
    assert NamedColor.MIDNIGHTBLUE.outline() == NamedColor.WHITE


def test_float_tuples():
    assert is_float_tuple((0.5, 0.0, 1.0))
    assert is_float_tuple((0.5, 0.0, 1.0, 1.0))
    assert is_float_tuple((0, 0, 0, 0))
    assert is_float_tuple((0, 0, 0, 1))
    assert is_float_tuple((0, 0, 1, 1))
    assert is_float_tuple((0, 1, 1, 1))
    assert is_float_tuple((1, 1, 1, 1))
    assert is_float_tuple((0, 0, 0))
    assert is_float_tuple((1, 1, 1))
    assert not is_float_tuple((2, 1, 1, 1))
    assert not is_float_tuple((0.5, 0.5, 0.5, 1.1))
    assert not is_float_tuple((0.5, 0.5, 1.1))
    assert not is_float_tuple((-0.1, 1, 1, 1))
    assert len(float_tuple((224, 238, 238))) == 3
    assert len(float_tuple((224, 238, 238, 99))) == 4
    with pytest.raises(ValueError) as e_info:
        _ = float_tuple((224, 238))
        assert e_info == "float_tuple() requires a 3-tuple or a 4-tuple, but a 2-tuple was given."
    with pytest.raises(ValueError) as e_info:
        _ = float_tuple((224, 238, 30, 40, 50))
        assert e_info == "float_tuple() requires a 3-tuple or a 4-tuple, but a 5-tuple was given."

    ft = float_tuple((224, 238, 238))
    assert is_float_tuple(ft)
    assert ft[0] < 1.0
    assert ft[1] < 1.0
    assert ft[2] < 1.0
    it = int_tuple(ft)
    assert it == (224, 238, 238)

    assert int_tuple((0, 0, 0)) == (0, 0, 0)
    assert int_tuple((0, 0, 0, 0)) == (0, 0, 0, 0)

    assert int_tuple((1, 1, 1)) == (255, 255, 255)
    assert int_tuple((1, 1, 1, 1)) == (255, 255, 255, 255)

    assert int_tuple((0.25, 0.5, 0.75)) == (63, 127, 191)
    assert int_tuple((0.25, 0.5, 0.75, 1.0)) == (63, 127, 191, 255)
    assert int_tuple((0.25, 0.5, 0.75, 0.999)) == (63, 127, 191, 255)


def test_color_outline():
    assert color_outline((0, 0, 0)) == (1, 1, 1)
    assert color_outline((4, 0, 0)) == (255, 255, 255)
    assert color_outline((0.1, 0, 0)) == (1, 1, 1)
    assert color_outline((230, 0, 0)) == (255, 255, 255)
    assert color_outline((230, 230, 0)) == (0, 0, 0)
    assert is_float_tuple((0.7, 0.8, 0))
    assert color_outline((0.7, 0.8, 0.2)) == (0, 0, 0)


def test_color_subdued():
    assert color_subdued((230, 230, 0)) == (115, 115, 0)
    assert color_subdued((4, 0, 0)) == (129, 127, 127)
    assert color_subdued((230, 0, 0)) == (242, 127, 127)

    assert int_tuple(color_subdued((0.7, 0.8, 0.2))) == (89, 102, 25)
    assert int_tuple(color_subdued((0.0, 0.0, 0.0))) == (127, 127, 127)
    assert int_tuple(color_subdued((0.1, 0, 0))) == (140, 127, 127)
