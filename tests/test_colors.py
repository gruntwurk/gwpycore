from gwpycore import NamedColor

def test_rgb():
    assert NamedColor.AZURE1.hex_format() == "#F0FFFF"
    # assert NamedColor.AZURE1.float_tuple() == (0.0, 0.0, 0.0, 1.0)
    # assert NamedColor.AZURE1.float_tuple(alpha=0.5) == (0.0, 0.0, 0.0, 0.5)
    assert NamedColor.by_name("azure1") == NamedColor.AZURE1
    assert NamedColor.by_name("azure") == NamedColor.AZURE1  # (1 suffix assumed)
    assert NamedColor.by_name("nosuch") == None
    assert NamedColor.by_value((240, 255, 255)) == NamedColor.AZURE1  # exact match
    assert NamedColor.by_value((241, 254, 254)) == NamedColor.AZURE1  # (being the closest match)
    assert NamedColor.by_value((241, 254, 250)) == NamedColor.MINTCREAM  # (being the closest match)
