from datetime import datetime
from gwpycore import timestamp

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
