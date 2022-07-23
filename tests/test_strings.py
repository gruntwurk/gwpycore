from gwpycore import (leading_spaces_count, normalize_name,
                      rstrip_special, strip_blank_lines, snake_case, camel_case)


def test_strip_blank_lines():
    lines = ["", "   ", "\t", "\t\t  ", "foo", "", "bar", "", "", ""]
    strip_blank_lines(lines)
    assert lines == ["foo", "", "bar"]


def test_rstrip_special():
    assert rstrip_special("nothing to strip") == "nothing to strip"
    assert rstrip_special("trailing spaces   ") == "trailing spaces"
    assert rstrip_special("trailing tabs\t\t") == "trailing tabs"
    assert rstrip_special("trailing newlines\n\n") == "trailing newlines"
    assert rstrip_special("trailing combo1 \t\n") == "trailing combo1"
    assert rstrip_special("trailing combo2\n\t  ") == "trailing combo2"
    assert rstrip_special("trailing combo3\n\n  ") == "trailing combo3"
    assert rstrip_special("trailing combo4   \t") == "trailing combo4"


def test_leading_spaces_count():
    assert leading_spaces_count("zero") == 0
    assert leading_spaces_count(" one") == 1
    assert leading_spaces_count("  two") == 2
    assert leading_spaces_count("   three") == 3
    assert leading_spaces_count("    four") == 4
    assert leading_spaces_count("\t zero plus tab") == 0
    assert leading_spaces_count(" \t one plus tab") == 1


def test_normalize_name():
    assert normalize_name("Plain123") == "Plain123"
    assert normalize_name("Percent%Sign") == "Percent_Sign"
    assert normalize_name("Percent%Sign", separator="~") == "Percent~Sign"
    assert normalize_name(" Leading and Middle Spaces") == "_Leading_and_Middle_Spaces"
    assert normalize_name(" Leading and Middle Spaces", separator="") == "LeadingandMiddleSpaces"


def test_camel_case():
    assert camel_case("something") == "Something"
    assert camel_case("some_thing") == "SomeThing"
    assert camel_case("some thing") == "Some thing"
    assert camel_case("SomeThing") == "Something"
    assert camel_case("") == ""


def test_snake_case():
    assert snake_case("SomeThing") == "some_thing"
    assert snake_case("someThing") == "some_thing"
    assert snake_case("some_thing") == "some_thing"
    assert snake_case("something") == "something"
    assert snake_case("") == ""

