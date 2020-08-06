import re

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
    r"dec(ember)?"]

def from_month_name(month_name:str) -> int:
    for month, name_pattern in enumerate(MONTH_NAMES):
        if re.match(name_pattern, month_name, re.IGNORECASE):
            return month+1
    return 0
