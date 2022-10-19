"""
Utilities for working with keyboard keystrokes.
"""
from typing import Dict, List, Tuple, Union

__all__ = [
    "parse_keystroke_expression",
    "generic_keystroke",
    "resolve_keybindings",
]


# These are the same key codes used by Kivy (as based off of pygame) -- with the
# addition of several aliases. For example, the "+" key has an alias of "plus"
# (which is how you have to refer to the plus key in a keystroke expression
# such as: shift+alt+plus).
KEYCODES = {
    # special keys
    'backspace': 8, 'tab': 9, 'enter': 13, 'rshift': 303, 'shift': 304,
    'alt': 308,  # aka. the Apple "Option" key
    'rctrl': 306, 'lctrl': 305,
    'super': 309,  # aka. meta, The Microsoft "Windows" key, aka. the Apple "Command" key
    'alt-gr': 307,  # The Alt-Graph key
    'compose': 311,
    'pipe': 310,
    'capslock': 301, 'escape': 27, 'spacebar': 32, 'pageup': 280,
    'pagedown': 281, 'end': 279, 'home': 278, 'left': 276, 'up':
    273, 'right': 275, 'down': 274, 'insert': 277, 'delete': 127,
    'numlock': 300, 'print': 144, 'screenlock': 145, 'pause': 19,

    # letters
    'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103,
    'h': 104, 'i': 105, 'j': 106, 'k': 107, 'l': 108, 'm': 109, 'n': 110,
    'o': 111, 'p': 112, 'q': 113, 'r': 114, 's': 115, 't': 116, 'u': 117,
    'v': 118, 'w': 119, 'x': 120, 'y': 121, 'z': 122,

    # digits
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,

    # numpad
    'numpad0': 256, 'numpad1': 257, 'numpad2': 258, 'numpad3': 259,
    'numpad4': 260, 'numpad5': 261, 'numpad6': 262, 'numpad7': 263,
    'numpad8': 264, 'numpad9': 265, 'numpaddecimal': 266,
    'numpaddivide': 267, 'numpadmul': 268, 'numpadsubstract': 269,
    'numpadadd': 270, 'numpadenter': 271,

    # F1-15
    'f1': 282, 'f2': 283, 'f3': 284, 'f4': 285, 'f5': 286, 'f6': 287,
    'f7': 288, 'f8': 289, 'f9': 290, 'f10': 291, 'f11': 292, 'f12': 293,
    'f13': 294, 'f14': 295, 'f15': 296,

    # other keys
    '(': 40, ')': 41,
    '[': 91, ']': 93,
    '{': 123, '}': 125,
    ':': 58, ';': 59,
    '=': 61, '+': 43,
    '-': 45, '_': 95,
    '/': 47, '*': 42,
    '?': 47,
    '`': 96, '~': 126,
    '´': 180, '¦': 166,
    '\\': 92, '|': 124,
    '"': 34, "'": 39,
    ',': 44, '.': 46,
    '<': 60, '>': 62,
    '@': 64, '!': 33,
    '#': 35, '$': 36,
    '%': 37, '^': 94,
    '&': 38, '¬': 172,
    '¨': 168, '…': 8230,
    'ù': 249, 'à': 224,
    'é': 233, 'è': 232,

    # aliases
    'plus': 43,  # + (how you have to refer to the + key in a keystroke expression, e.g. shift+alt+plus)
    # and just to be consistent...
    'minus': 45,  # -
    'times': 42,  # *
    'divide': 47,  # /
    # alternate spellings/abbreviations
    'lshift': 304,  # shift
    'ctrl': 305,  # lctrl
    'esc': 27,  # escape
    'bksp': 8,  # backspace
    'return': 13,  # enter
    'space': 32,   # spacebar
    'pgup': 280,  # pageup
    'pgdn': 281,  # pagedown
    'ins': 277,  # insert
    'del': 127,  # delete
}

# A mapping of specific keys to their generic equivalent.
KEYCODE_GENERICS = {
    'numpad0': '0',
    'numpad1': '1',
    'numpad2': '2',
    'numpad3': '3',
    'numpad4': '4',
    'numpad5': '5',
    'numpad6': '6',
    'numpad7': '7',
    'numpad8': '8',
    'numpad9': '9',
    'numpaddecimal': '.',
    'numpaddivide': '/',
    'numpadmul': '*',
    'numpadsubstract': '-',
    'numpadadd': '+',
    'numpadenter': 'enter',
}

KEYCODE_GENERICS_BY_NUM = {KEYCODES[key]: KEYCODES[value] for key, value in KEYCODE_GENERICS.items()}

# FIXME What other modifiers are there?
MODIFIERS = {
    'shift': 304,
    'ctrl': 305,
    'alt': 308,
    'opt': 308,
    'meta': 309,
    'super': 309,
}


def parse_keystroke_expression(keystroke_expression: Union[List, str], as_generic: False) -> List[int]:
    """
    Parses a key combination expression, i.e. key identifiers separated by a
    plus-sign (+). Key identifiers are either single characters representing a
    keyboard key, such as "a" or "=", or special key names such as "plus", "enter",
    "backspace", "tab", "rshift", or modifiers such as "shift", "ctrl". Key identifiers
    are case-insensitive.

    :param keystroke_expression: e.g. `shift+alt+plus` or as a list:  [`shift', 'alt', 'plus`].
    All but the last one must be one of the four modifiers (`shift`, `ctrl`,` alt` or `opt`,
    `meta` or `super`).

    :param as_generic: True if specific keys such as "numpadsubstract" should be treated as
    their generic equivalent ("-"). Defaults to False.

    :return: A list of integers, sorted from low to high. For example, `shift+alt+plus`
    `alt+shift+plus` and `shift+plus+alt` all return `[43, 304, 308]`

    :raises ValueError: If a part of the expression is invalid.
    """
    if isinstance(keystroke_expression, List):
        parts = [key_str.casefold() for key_str in keystroke_expression]
    else:
        parts = keystroke_expression.casefold().split("+")

    if len(parts) == 0:
        return []

    if as_generic:
        if parts[-1] in KEYCODE_GENERICS:
            parts[-1] = KEYCODE_GENERICS[parts[-1]]
    try:
        key_ints = [KEYCODES[parts[-1]]]
        for part in parts[:-1]:
            key_ints.append(KEYCODES[part])
    except IndexError:
        raise ValueError(keystroke_expression)

    return sorted(key_ints)


def generic_keystroke(actual_keystroke: Tuple[int]) -> Tuple[int]:
    """
    Converts a tuple that represents a keystroke (combination) and returns the generic equivalent.
    For example (260, 305) (i.e. "ctrl+numpad4") becomes (52, 305) (i.e. "ctrl+4").

    :param actual_keystroke: A tuple of keystrokes (integers).

    :return: The converted tuple (or the same tuple if there was nothing to convert), or None.
    """
    if not actual_keystroke:
        return None
    generic = actual_keystroke
    for i, part in enumerate(generic):
        if part in KEYCODE_GENERICS_BY_NUM:
            generic[i] = KEYCODE_GENERICS_BY_NUM[part]
    return generic


def resolve_keybindings(raw_keybindings: Dict) -> Dict:
    """
    Converts a dictionary of keystroke expression strings (keyed by action
    names) to a dictionary that is keyed by the resolved keystroke expression
    and gives the action name as the value. For example, if your configuration
    INI file contains a section of keymappings

    [keymap]
    print_analysis = ctrl+shift+f7
    add_customer = alt+a

    and you use GWConfigParser's section_as_dict() method to read it in,

    Then passing that dict into this function yields:

    {
        (288, 304, 305): 'print_analysis',
        (97, 308): 'add_customer',
    }

    :param raw_keybindings: A dictionary of keystroke expression strings (keyed
    by action names).

    :return: A dictionary that is keyed by the resolved keystroke expression
    and gives the action name as the value.
    """
    bindings = {}
    for key, value in raw_keybindings.items():
        bindings[parse_keystroke_expression(value)] = key
    return bindings


