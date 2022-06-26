from gwpycore import as_color, as_named_color, NamedColor

def test_as_color():
    assert as_color((1,2,3)) == (1,2,3)
    assert as_color("#FF0088") == (255,0,136)
    assert as_color("FF0088") is None
    assert as_color("#FF00") is None
    assert as_color("(4,5,6)") == (4,5,6)
    assert as_color("7,8,9") == (7,8,9)


def test_as_named_color():
    assert as_named_color("#F0FFFF") == NamedColor.AZURE1
    assert as_named_color("F0FFFF") == NamedColor.AZURE1
    assert as_named_color("#F0FF") is None
    assert as_named_color("azure1") == NamedColor.AZURE1
    assert as_named_color("azure") == NamedColor.AZURE1  # (1 suffix assumed)
    assert as_named_color("nosuch") == None
    assert as_named_color("(240,255,255)") == NamedColor.AZURE1  # exact match
    assert as_named_color("(240, 255, 255)") == NamedColor.AZURE1  # exact match
    assert as_named_color("240,255,255") == NamedColor.AZURE1  # exact match
    assert as_named_color("241, 254, 254") == NamedColor.AZURE1  # (being the closest match)
    assert as_named_color("241, 254, 250") == NamedColor.MINTCREAM  # (being the closest match)
