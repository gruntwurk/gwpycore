from gwpycore import fuzzy_and, fuzzy_or, fuzzy_english

def test_fuzzy_english():
    assert fuzzy_english(b'') == ""
    assert fuzzy_english(b'\x00') == "false"
    assert fuzzy_english(b'\xFF') == "true"
    assert fuzzy_english(b'\xF1') == "true"
    assert fuzzy_english(b'\x85') == "maybe"
    assert fuzzy_english(b'\x85') == "maybe"
    assert fuzzy_english(b'\xDF') == "true enough"
    assert fuzzy_english(b'\xC9') == "highly probable"
    assert fuzzy_english(b'\xB2') == "probable"
    assert fuzzy_english(b'\xAF') == "maybe"
    assert fuzzy_english(b'\x50') == "maybe"
    assert fuzzy_english(b'\x45') == "doubtful"
    assert fuzzy_english(b'\x31') == "highly doubtful"
    assert fuzzy_english(b'\x20') == "false enough"


def test_fuzzy_and():
    assert fuzzy_and(b'') == 0
    assert fuzzy_and(b'\x00') == b'\x00'[0]
    assert fuzzy_and(b'\xFF') == b'\xFF'[0]
    assert fuzzy_and(b'\xAB') == b'\xAB'[0]
    assert fuzzy_and(b'\x00\xFF') == b'\x00'[0]
    assert fuzzy_and(b'\xFF\x00') == b'\x00'[0]
    assert fuzzy_and(b'\xFF\xAB') == b'\xAB'[0]
    assert fuzzy_and(b'\xFF\xAB\xCC') == b'\xAB'[0]

def test_fuzzy_or():
    assert fuzzy_or(b'') == 0
    assert fuzzy_or(b'\x00') == b'\x00'[0]
    assert fuzzy_or(b'\xFF') == b'\xFF'[0]
    assert fuzzy_or(b'\xAB') == b'\xAB'[0]
    assert fuzzy_or(b'\x00\xFF') == 255
    assert fuzzy_or(b'\xFF\x00') == 255
    assert fuzzy_or(b'\xFF\xAB') == 255
    assert fuzzy_or(b'\xFF\xAB\xCC') == 255
    assert fuzzy_or(b'\x00\xAB\xCC') == b'\xCC'[0]
    assert fuzzy_or(b'\x00\xAB\x99') == b'\xAB'[0]

