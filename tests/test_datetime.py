from datetime import datetime
import time
from gwpycore import timestamp, as_datetime


def test_timestamp():
    sometime = datetime.strptime("30 Jun 20 13:59:59", "%d %b %y %H:%M:%S")
    assert timestamp(sometime) == "2020_06_30_135959"
    assert timestamp(sometime, format="%Y%m%d%H%M%S") == "20200630135959"
    assert timestamp(sometime, format="%Y%m%d") == "20200630"
    assert timestamp(sometime, format="%Y-%m-%d-%H%M%S") == "2020-06-30-135959"
    assert timestamp(sometime, format="%Y/%m/%d_%H%M%S") == "2020/06/30_135959"

    # Typical usage is to call it without a specific time and let it use the current date/time
    # since we don't know what this time is, we can atl east make sure the result is a str of the expected lengh
    assert len(timestamp()) == len("2020_06_30_135959")
    assert len(timestamp(format="%Y%m%d%H%M%S")) == len("20200630135959")


def test_as_datetime():
    someday = datetime.strptime("30 Jun 20", "%d %b %y")
    sometime = datetime.strptime("30 Jun 20 13:59:59", "%d %b %y %H:%M:%S")
    assert as_datetime(sometime) == sometime
    assert as_datetime(0.0) == datetime(1970, 1, 1, 0, 0, 0)
    assert as_datetime(1.0) == datetime(1970, 1, 1, 0, 0, 1)
    assert as_datetime(1) == datetime(1970, 1, 1, 0, 0, 1)
    assert as_datetime("30 Jun 20 13:59:59") == sometime
    assert as_datetime("30 Jun 20") == someday
    assert as_datetime("   30 Jun 20") == someday
    assert as_datetime("   30 Jun 20   ") == someday
    assert as_datetime("30 Jun 20   ") == someday
    assert as_datetime("30 Jun 2020   ") == someday
