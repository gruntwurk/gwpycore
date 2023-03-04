from gwpycore import color_parse


def test_color_parse():
    assert color_parse("#FFFFFF") == (0, 0, 0)
