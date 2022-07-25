from gwpycore import as_color, as_named_color, NamedColor, GlobalSettings


def test_as_color():
    assert as_color((1, 2, 3)) == (1, 2, 3)
    assert as_color("#FF0088") == (255, 0, 136)
    assert as_color("FF0088") is None
    assert as_color("#FF00") is None
    assert as_color("(4,5,6)") == (4, 5, 6)
    assert as_color("7,8,9") == (7, 8, 9)


def test_as_named_color():
    assert as_named_color("#F0FFFF") == NamedColor.AZURE
    assert as_named_color("F0FFFF") == NamedColor.AZURE
    assert as_named_color("#F0FF") is None
    assert as_named_color("AZURE") == NamedColor.AZURE
    assert as_named_color("azure") == NamedColor.AZURE  # (1 suffix assumed)
    assert as_named_color("nosuch") is None
    assert as_named_color("(240,255,255)") == NamedColor.AZURE  # exact match
    assert as_named_color("(240, 255, 255)") == NamedColor.AZURE  # exact match
    assert as_named_color("240,255,255") == NamedColor.AZURE  # exact match
    assert as_named_color("241, 254, 254") == NamedColor.AZURE  # (being the closest match)
    assert as_named_color("241, 254, 250") == NamedColor.MINTCREAM  # (being the closest match)


def test_key_transform():
    CONFIG = GlobalSettings()
    CONFIG["hyphenated-key"] = "hyphenated"
    CONFIG["underscored_key"] = "underscored"
    assert CONFIG["hyphenated-key"] == "hyphenated"
    assert CONFIG["underscored-key"] == "underscored"
    assert CONFIG["underscored_key"] == "underscored"

    CONFIG["hyphenated-attr"] = "hyphenated"
    CONFIG.underscored_attr = "underscored"
    assert CONFIG.hyphenated_attr == "hyphenated"
    assert CONFIG.underscored_attr == "underscored"


def test_immutable():
    outdated = {"front_door": "painted", "back_door": "sliding"}
    set_in_stone = {"flooring": "granite", "countertop": "marble"}
    CONFIG = GlobalSettings()
    CONFIG.update(outdated)
    CONFIG.update_as_immutable(set_in_stone)
    assert "flooring" in CONFIG.__immutables__
    assert "countertop" in CONFIG.__immutables__

    CONFIG.flooring = "carpet"  # should be ignored
    CONFIG["countertop"] = "slate"  # should be ignored

    CONFIG.walls = "white"
    CONFIG["ceiling"] = "beige"
    CONFIG.back_door = "French"

    assert CONFIG.front_door == "painted"
    assert CONFIG.back_door == "French"
    assert CONFIG.countertop == "marble"
    assert CONFIG.flooring == "granite"
    assert CONFIG.walls == "white"
    assert CONFIG.ceiling == "beige"

