import re


def strip_blank_lines(lines: list):
    """Strips blank lines from the top and bottom of a list of strings"""
    if lines:
        while re.match(r"^\s*$", lines[0]):
            lines.pop(0)
        while re.match(r"^\s*$", lines[-1]):
            lines.pop()


def rstrip_special(line, JUNK="\n \t"):
    """
    Returns the given line stripped of specific trailing characters
    (spaces, tabs, and newlines by default).

    Note that line.rstrip() would also strip sundry control characters,
    the loss of which can interfere with Emacs editing, for one thing.

    (Used by tab-to-spaces converter code, for example.)
    """
    i = len(line)
    while i > 0 and line[i - 1] in JUNK:
        i -= 1
    return line[:i]


def leading_spaces_count(line):
    """
    (Used by tab-to-spaces converter code, for example.)
    """
    i, n = 0, len(line)
    while i < n and line[i] == " ":
        i += 1
    return i


def normalize_name(name, separator="_"):
    """Normalizes a name by replacing all non-alphanumeric characters with underscores."""
    return re.sub("[^A-Za-z0-9_]+", separator, name)


def classify_text(pattern_list, text: str) -> any:
    """
    Runs through a list of regex patterns in an attempt to classify the given text.
    pattern_list is a list of tuples where the first value is the pattern and the second is the corresponding classification.
    If any one of the patterns in the list is found within the text, then the corresponding key is returned as the classification.
    If nothing matches, then None is returned.
    """
    for (pattern, candidate_classification) in pattern_list:
        if re.search(pattern, text):
            return candidate_classification
    return None


__all__ = ("strip_blank_lines", "rstrip_special", "leading_spaces_count", "normalize_name", "classify_text")
