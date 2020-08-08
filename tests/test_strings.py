from gwpycore.gw_strings import strip_blank_lines, phonetic_spelling


def test_strip_blank_lines():
    lines = ["", "   ", "\t", "\t\t  ", "foo", "", "bar", "", "", ""]
    strip_blank_lines(lines)
    assert lines == ["foo", "", "bar"]


def test_phonetic_spelling():
    assert phonetic_spelling("K6NNL") == "Kilo 6 November November Lima"
