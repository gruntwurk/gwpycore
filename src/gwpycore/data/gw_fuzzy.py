from enum import IntEnum
from typing import Union

__all__ = ("fuzzy_and", "fuzzy_or", "fuzzy_english")


Fuzzy = Union[bytearray, bytes, int]


class FuzzyStep(IntEnum):
    """Enumeration of fuzziness, in general."""
    TRUE_ABSOLUTELY = 15
    TRUE = 14
    TRUE_ENOUGH = 13
    HIGHLY_PROBABLE = 12
    PROBABLE = 11
    SHOULD_BE = 10
    COULD_BE = 9
    MAYBE = 8
    ALMOST_EVEN = 7
    UNSURE = 6
    MAYBE_NOT = 5
    DOUBTFUL = 4
    HIGHLY_DOUBTFUL = 3
    FALSE_ENOUGH = 2
    FALSE = 1
    FALSE_ABSOLUTELY = 0

    @classmethod
    def possibleValues(cls) -> str:
        return ", ".join([e.name for e in cls])

    @classmethod
    def displayNames(cls):
        return {cls.TRUE_ABSOLUTELY: "true",
                cls.TRUE: "true",
                cls.TRUE_ENOUGH: "true enough",
                cls.HIGHLY_PROBABLE: "highly probable",
                cls.PROBABLE: "probable",
                cls.SHOULD_BE: "maybe",
                cls.COULD_BE: "maybe",
                cls.MAYBE: "maybe",
                cls.ALMOST_EVEN: "maybe",
                cls.UNSURE: "maybe",
                cls.MAYBE_NOT: "maybe",
                cls.DOUBTFUL: "doubtful",
                cls.HIGHLY_DOUBTFUL: "highly doubtful",
                cls.FALSE_ENOUGH: "false enough",
                cls.FALSE: "false",
                cls.FALSE_ABSOLUTELY: "false"}

    def displayName(self) -> str:
        return FuzzyStep.displayNames()[self]


class FuzzyError(Exception):
    pass


def fuzzy_and(fuzzies: Fuzzy) -> int:
    """
    Reduces the given fuzzies string (bytes-like) to a single byte that is
    the "AND" of all of the bytes (namely, the lowest value).
    If fuzzies is empty, then the result remains empty.
    """
    if isinstance(fuzzies, int):
        return fuzzies
    if len(fuzzies) == 0:
        return 0
    if len(fuzzies) == 1:
        return fuzzies[0]
    lowest = 256
    for b in fuzzies:
        if b < lowest:
            lowest = b
    return lowest


def fuzzy_or(fuzzies: Fuzzy) -> int:
    """
    Reduces the given fuzzies string (bytes-like) to a single byte that is
    the "OR" of all of the bytes (namely, the highest value).
    If fuzzies is empty, then the result remains empty.
    """
    if isinstance(fuzzies, int):
        return fuzzies
    if len(fuzzies) == 0:
        return 0
    if len(fuzzies) == 1:
        return fuzzies[0]
    highest = 0
    for b in fuzzies:
        if int(b) > highest:
            highest = int(b)
    return highest


def fuzzy_english(fuzzy: Fuzzy) -> str:
    if len(fuzzy) < 1:
        return ""
    if len(fuzzy) > 1:
        raise FuzzyError(f'Expected a single fuzzy value but was given {len(fuzzy)}')
    return FuzzyStep(int(fuzzy[0] / 16)).displayName()


