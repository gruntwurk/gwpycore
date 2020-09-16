from gwpycore import as_color

def test_as_color():

    assert as_color((1,2,3)) == (1,2,3)
    assert as_color("#FF0088") == (255,0,136)
    assert as_color("FF0088") is None
    assert as_color("#FF00") is None
    assert as_color("(4,5,6)") == (4,5,6)
    assert as_color("7,8,9") == (7,8,9)


