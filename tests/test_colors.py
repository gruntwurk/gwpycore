from gwpycore import NamedColor

def test_NamedColor_construction():
    assert NamedColor.by_value("#F0FFFF") == NamedColor.AZURE
    assert NamedColor.by_value("F0FFFF") == NamedColor.AZURE

    assert NamedColor.by_name("azure") == NamedColor.AZURE
    assert NamedColor.by_name("nosuch") == None

    assert NamedColor.by_value(240, 255, 255) == NamedColor.AZURE  # exact match
    assert NamedColor.by_value(241, 254, 253) == NamedColor.AZURE  # (being the closest match)
    assert NamedColor.by_value(241, 254, 253, only_standard=True) == NamedColor.AZURE  # (being the closest match)
    assert NamedColor.by_value(241, 254, 250) == NamedColor.MINTCREAM  # (being the closest match)

    rgb = (156, 102, 31)
    assert NamedColor.by_value(rgb) == NamedColor.BRICK  # exact match allowing for non-standard colors
    assert NamedColor.by_value(156, 102, 31, only_standard=True) == NamedColor.SIENNA # closest match sticking to standard colors
    assert NamedColor.by_value(*rgb, only_standard=True) == NamedColor.SIENNA # closest match sticking to standard colors


def test_NamedColor_methods():
    assert NamedColor.AZURE.hex_format() == "#F0FFFF"
    # assert NamedColor.AZURE1.float_tuple() == (0.0, 0.0, 0.0, 1.0)
    # assert NamedColor.AZURE1.float_tuple(alpha=0.5) == (0.0, 0.0, 0.0, 0.5)
    assert NamedColor.BLACK.is_standard()
    assert not NamedColor.TURQUOISEBLUE.is_standard()

    assert NamedColor.MINTCREAM.brightness() == 250
    assert NamedColor.MINTCREAM.gray_version() == NamedColor.GRAY98
    assert NamedColor.MINTCREAM.lighter() == NamedColor.GRAY98
    assert NamedColor.MINTCREAM.darker() == NamedColor.INDIANRED4
    assert NamedColor.MINTCREAM.subdued() == NamedColor.INDIANRED4
    assert NamedColor.MINTCREAM.outline() == NamedColor.BLACK

    assert NamedColor.MIDNIGHTBLUE.brightness() == 54
    assert NamedColor.MIDNIGHTBLUE.gray_version() == NamedColor.GRAY21
    assert NamedColor.MIDNIGHTBLUE.lighter() == NamedColor.AQUAMARINE
    assert NamedColor.MIDNIGHTBLUE.darker() == NamedColor.GRAY3
    assert NamedColor.MIDNIGHTBLUE.subdued() == NamedColor.AQUAMARINE
    assert NamedColor.MIDNIGHTBLUE.outline() == NamedColor.WHITE



