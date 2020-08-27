import time

from gwpycore import timestamp


def test_timestamp():
    currentTime = time.strptime("30 Jun 20 13:59:59", "%d %b %y %H:%M:%S")
    assert timestamp(currentTime) == "2020_06_30_135959"
    assert timestamp(currentTime, separator="") == "20200630135959"
    assert timestamp(currentTime, separator="-") == "2020-06-30-135959"
