import re
import distutils
import string
import random
from typing import Optional

# ############################################################################
# Since distutils is deprecated...                   ARGUMENT PROCESSING UTILS
# ############################################################################


def split_quoted(s):
    """
    Split a string up according to Unix shell-like rules for quotes and
    backslashes. In short: words are delimited by spaces, as long as those
    spaces are not escaped by a backslash, or inside a quoted string. Single
    and double quotes are equivalent, and the quote characters can be
    backslash-escaped. The backslash is stripped from any two-character
    escape sequence, leaving only the escaped character. The quote
    characters are stripped from any quoted string. Returns a list of words.
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    return distutils.util.split_quoted(s)


# ###########################################################################
#                                                         TEXT CASE FUNCTIONS
# ###########################################################################

def snake_case(identifier: str) -> str:
    """
    Converts CamelCase or javaCase to snake_case (all lower with underscores).

    See also: `camel_case(), normalize_name()`
    """
    words = re.findall(r"([a-z]+|[A-Z][a-z]*|[^A-Za-z]+)", identifier)
    lower_words = [word.lower() for word in words if word != "_"]
    return "_".join(lower_words)


def camel_case(identifier: str) -> str:
    """
    Converts snake_case to CamelCase.
    """
    if not identifier:
        return ""
    words = identifier.split('_')
    camel_words = [word[0].upper() + word[1:].lower() for word in words]
    return "".join(camel_words)


# ############################################################################
#                                                             ADDITIONAL UTILS
# ############################################################################


def as_text(input: any) -> Optional[str]:
    """
    A string converter for use with ConfigParser. Note: This is the same as a
    plain ConfigParser.get(), but conforms to the signature as all of the
    other as_X getters.
    """
    return str(input)


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


def normalize_name(name, separator="_") -> str:
    """
    Normalizes a name by replacing all non-alphanumeric characters with
    underscores (or whatever separator you specify).

    See also: `snake_case(), camel_case()`.
    """
    return re.sub("[^A-Za-z0-9_]+", separator, name)


def classify_text(pattern_list, text: str) -> any:
    """
    Runs through a list of regex patterns in an attempt to classify the given
    text. pattern_list is a list of tuples where the first value is the
    pattern and the second is the corresponding classification. If any one of
    the patterns in the list is found within the text, then the corresponding
    key is returned as the classification. If nothing matches, then None is
    returned.
    """
    for (pattern, candidate_classification) in pattern_list:
        if re.search(pattern, text):
            return candidate_classification
    return None


def random_token(length=30, choices=string.ascii_lowercase) -> str:
    return ''.join(random.choice(choices) for i in range(length))


def formatted_phone_number(orig_phone: str) -> str:
    """
    Returns a formatted phone number.

    :param phone: Currently only understands 10-digit phone numbers of the North
                  American Numbering Plan (NANP).
    """
    if not orig_phone:
        return ''
    phone = re.sub(r"[^\d]", "", orig_phone)
    if phone.startswith("1"):
        phone = phone[1:]
    if len(phone) != 10:
        return orig_phone
    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"


__all__ = [
    "split_quoted",
    "strip_blank_lines",
    "rstrip_special",
    "leading_spaces_count",
    "normalize_name",
    "classify_text",
    "snake_case",
    "camel_case",
    "as_text",
    "random_token",
    "formatted_phone_number",
]

