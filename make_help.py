"""
Scan thru a Makefile, looking for target definitions that have a special trailing comment
(one that starts with two #'s), and consider that comment to be the help text.
"""

import re
import sys

print("")
for line in sys.stdin:
    if match := re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line):
        target, help = match.groups()
        print("%-20s %s" % (target, help))
