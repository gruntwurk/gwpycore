import re

PHONETIC_LIST = [
    "Alpha",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
    "Golf",
    "Hotel",
    "India",
    "Juliet",
    "Kilo",
    "Lima",
    "Mike",
    "November",
    "Oscar",
    "Papa",
    "Quebec",
    "Romeo",
    "Sierra",
    "Tango",
    "Uniform",
    "Victor",
    "Whiskey",
    "Xray",
    "Yankee",
    "Zulu",
]
PHONETIC_DICT = {
    "A": "Alpha",
    "B": "Bravo",
    "C": "Charlie",
    "D": "Delta",
    "E": "Echo",
    "F": "Foxtrot",
    "G": "Golf",
    "H": "Hotel",
    "I": "India",
    "J": "Juliet",
    "K": "Kilo",
    "L": "Lima",
    "M": "Mike",
    "N": "November",
    "O": "Oscar",
    "P": "Papa",
    "Q": "Quebec",
    "R": "Romeo",
    "S": "Sierra",
    "T": "Tango",
    "U": "Uniform",
    "V": "Victor",
    "W": "Whiskey",
    "X": "Xray",
    "Y": "Yankee",
    "Z": "Zulu",
}


def strip_blank_lines(lines: list):
    """Strips blank lines from the top and bottom of a list of strings"""
    if lines:
        while re.match(r"^\s*$", lines[0]):
            lines.pop(0)
        while re.match(r"^\s*$", lines[-1]):
            lines.pop()


def phonetic_spelling(callsign):
    translation = []
    for char in callsign:
        if char in PHONETIC_DICT:
            translation.append(PHONETIC_DICT[char])
        else:
            translation.append(char)
    return " ".join(translation)
