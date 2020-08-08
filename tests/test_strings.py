from gwpycore.gw_strings import phonetic_spelling, strip_blank_lines


def test_strip_blank_lines():
    lines = ["", "   ", "\t", "\t\t  ", "foo", "", "bar", "", "", ""]
    strip_blank_lines(lines)
    assert lines == ["foo", "", "bar"]


def test_phonetic_spelling():
    assert phonetic_spelling("K6NNL") == "Kilo 6 November November Lima"
