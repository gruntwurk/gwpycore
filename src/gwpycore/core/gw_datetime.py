import re
from datetime import date, datetime, timedelta
from typing import Tuple
from dateutil.parser import parse

MONTH_NAMES = [
    r"jan(uary)?",
    r"feb(uary)?",
    r"mar(ch)?",
    r"apr(il)?",
    r"may",
    r"jun(e)?",
    r"jul(y)?",
    r"aug(ust)?",
    r"sep(t)?(ember)?",
    r"oct(ober)?",
    r"nov(ember)?",
    r"dec(ember)?",
]
VALID_DATE_RANGES = "TODAY | YESTERDAY | T-n | yyyy | yyyyQn"
DATE_RANGE_PATTERN = r"TODAY|YESTERDAY|T-\d+|\d{2}\/\d{2}\/\d{4}|\d{2}\/\d{4}|Q[1234]\/\d{4}|\d{4}Q[1234]|\d{4}"
ONE_DAY = timedelta(days=1)
ONE_MILLISECOND = timedelta(milliseconds=1)
TIME_OF_DAY_PATTERN = r"^(\d\d)[:]?(\d\d)\s*([AaPp]?)"


def parse_time(s) -> datetime:
    if not s:
        return None
    try:
        ret = parse(s)
    except ValueError:
        ret = datetime.utcfromtimestamp(float(s))
    return ret


def from_month_name(month_name: str) -> int:
    """
    Converts the given month name to the appropriate number (1-based).
    Casing is ignored.
    The month name can be spelled out just the first 3 letters.
    September can also be abbreviated to 4 letters.
    Returns 0 if the month name is invalid.
    """
    for month, name_pattern in enumerate(MONTH_NAMES):
        if re.match(name_pattern, month_name, re.IGNORECASE):
            return month + 1
    return 0


def timestamp(the_time: datetime = None, format="%Y_%m_%d_%H%M%S") -> str:
    """
    Returns a string suitable for appending to a filename, for example, as a timestamp.
    """
    if not the_time:
        the_time = datetime.now()
    return the_time.strftime(format)


def date_from_vague_parts(
    year: str, month: str, day: str, time_of_day: str
) -> datetime:
    """
    Combines the given string arguments into a datetime value.
    year -- A string with 2 or 4 digits. 00-49 are assumed to be 2000-2049. 50-99 are 1950-1999)
    month -- A string with either the month name or month number.
    day -- A string with 1 or 2 digits.
    time_of_day -- (empty) or 23:59, 2359, 12:59P, 1200A
    """
    y = int(year)
    if y < 50:
        y += 2000
    elif y < 100:
        y += 1900

    if month.isdigit():
        m = int(month)
    else:
        m = from_month_name(month)

    d = int(day)

    h = 0
    min = 0
    if (m := re.match(TIME_OF_DAY_PATTERN, time_of_day)) :
        h: int = int(m.group(1))
        min: int = int(m.group(2))
        modifier: str = "" if not m.group(3) else m.group(3).lower()
        if modifier == "p" and h < 12:
            h += 12
        elif modifier == "a" and h == 12:
            h = 0
    return datetime(y, m, d, h, min)


def start_of_quarter(year: int, quarter: int) -> datetime:
    m = quarter * 3 - 3
    return date(year, m, 1)


def end_of_quarter(year: int, quarter: int) -> datetime:
    m = quarter * 3 - 1
    d = 30 if quarter in [2, 3] else 31
    return date(year, m, d)


def interpret_date_range(arg: str) -> Tuple[datetime, datetime]:
    """
    Interprets certain English terms that refer to date/time ranges.
    Returns a tuple of two datetimes for the start and end of the range.

    "TODAY" -- (today at 00:00 through today at 11:59:59.9999)
    "YESTERDAY" -- (yesterday at 00:00 through yesterday at 11:59:59.9999)
    "T-n" -- (n days ago at 00:00 through n days ago at 11:59:59.9999)
    "2020Q2" -- (Mar 1, 2020 through May 30, 2020)
    "2020" -- (Jan 1, 2020 through Dec 31, 2020)
    """
    start: datetime = None
    end: datetime = None
    arg = arg.upper()
    if (m := re.match(DATE_RANGE_PATTERN, arg)) :
        if arg == "TODAY":
            start = date.today()
            end = start + ONE_DAY - ONE_MILLISECOND
        elif arg == "YESTERDAY":
            start = date.today() - ONE_DAY
            end = start + ONE_DAY - ONE_MILLISECOND
        elif arg.startswith("T-"):
            days_back = int(arg[2:])
            start = date.today() - timedelta(days=days_back)
            end = start + ONE_DAY - ONE_MILLISECOND
        elif "Q" in arg:
            (year, letter, quarter) = arg.partition("Q")
            y = int(year)
            q = int(quarter)
            start = start_of_quarter(y, q)
            end = end_of_quarter(y, q)
        elif arg.isdigit():
            y = int(arg)
            start = start_of_quarter(y, 1)
            end = end_of_quarter(y, 4)
    return (start, end)


__all__ = [
    "parse_time",
    "date_from_vague_parts",
    "end_of_quarter",
    "from_month_name",
    "interpret_date_range",
    "start_of_quarter",
    "timestamp"
]
