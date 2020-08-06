from gwpycore.gw_datetime import from_month_name

def test_from_month_name():
    assert from_month_name("Jan") == 1
    assert from_month_name("jan") == 1
    assert from_month_name("january") == 1
    assert from_month_name("January") == 1
    assert from_month_name("dec") == 12
    assert from_month_name("Dec") == 12
    assert from_month_name("december") == 12
    assert from_month_name("December") == 12
