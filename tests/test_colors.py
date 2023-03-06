from gwpycore import color_parse, HTML_COLORS

syntax_scheme = {
    'normal': (0, 0, 0, 0),  # Invisible
    'comment': (48, 48, 48),
    'bold': HTML_COLORS['green'],
    'italics': (*HTML_COLORS['yellow'], 128),  # Translucent
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
