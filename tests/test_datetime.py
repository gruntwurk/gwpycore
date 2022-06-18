from datetime import datetime
from gwpycore import timestamp

def test_timestamp():
    currentTime = datetime.strptime("30 Jun 20 13:59:59", "%d %b %y %H:%M:%S")
    assert timestamp(currentTime) == "2020_06_30_135959"
    assert timestamp(currentTime, format="%Y%m%d%H%M%S") == "20200630135959"
    assert timestamp(currentTime, format="%Y-%m-%d-%H%M%S") == "2020-06-30-135959"
    assert timestamp(currentTime, format="%Y/%m/%d_%H%M%S") == "2020/06/30_135959"
