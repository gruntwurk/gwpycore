import contextlib
from enum import Enum
from typing import List

from .exceptions import GWValueError

__all__ = [
    'enum_default_value',
    'enum_by_name',
]


# ############################################################################
#                                                                       GWEnum
# ############################################################################

class GWEnum(Enum):
    """
    Base class for an `Enum` that, among other things, provides all the
    neccesary suuport for being used with the `GWDropdownEnum` Kivy widget.
    Enum values that are tuples have special treatment.

    Added methods:
        * `display_name()` (and its alias `description()`) -> str
        * `value_count` -> int
        * `primary_value`
        * `secondary_values` (plural) -> tuple
        * `secondary_value` (singlular)
        * (class) `possible_values` -> list(str)
        * (class) `by_name` -> (enum member)
        * (class) `by_value`, -> (enum member)
        * (class) `default` -> (enum member)
    """

    def display_name(self) -> str:
        """
        How to describe this member to the user (e.g. as a choice in a dropdown
        (spinner) widget.

        :return: The primary value, if it's a string; otherwise, the member name.
        """
        primary = self.primary_value()
        return primary if isinstance(primary, str) else self.name

    def description(self) -> str:
        """
        Alias for display_name().
        """
        return self.display_name()

    def value_count(self) -> int:
        """
        If the value is a tuple, then the value count is the length of the
        tuple; otherwise 1.

        NOTE: Override this method to always return 1 if the value is a tuple
        but should be treated as a single value (e.g. an RGB color).
        """
        # IMPORTANT: We are specifically testing for `tuple` type on purpose
        # (as opposed to `iterable`) becasue `iterable` includes `str`.
        # And also because Enum values are immutable, so expressing the value
        # as a `list` (as opposed to  a `tuple`) makes no sense.
        # TODO Test if a list value gets converted to a tuple.
        return len(self.value) if isinstance(self.value, tuple) else 1

    def primary_value(self):
        """
        If the value is a tuple, then the first elemnent of the tuple is
        considered to be the primary value while all other elements of the
        tuple are considered to be secondary.

        :return: `value`, or `value[0]` (if value is a tuple).
        """
        return self.value if self.value_count() == 1 else self.value[0]

    def secondary_values(self) -> tuple:
        """
        The value tuple without the first element (if the value is a tuple).

        If the value is a tuple, then the first elemnent of the tuple is
        considered to be the primary value while all other elements of the
        tuple are considered to be secondary.

        :return: `None`, or `value[1:]` (if value is a tuple).
        """
        return None if self.value_count() == 1 else self.value[1:]

    def secondary_value(self):
        """
        The one next value after the primary value, if any.

        If the value is a tuple, then the first elemnent of the tuple is
        considered to be the primary value while all other elements of the
        tuple are considered to be secondary.

        :return: `None` or `value[1]` (if value is a tuple).
        """
        return None if self.value_count() == 1 else self.value[1]

    @classmethod
    def possible_values(cls) -> List[str]:
        """
        A list describing the elements, in the order defined. The primary
        value is used if it is a string; otherise, the element's name is used.
        """
        return [e.display_name() for e in cls]

    @classmethod
    def by_value(cls, value):
        if not value:
            return cls.default()
        if isinstance(value, str):
            value = value.strip().casefold()
        for e in cls:
            if value in [e.primary_value(), str(e.primary_value()).casefold(), e.name.casefold()]:
                return e
        raise GWValueError(f"No such {cls.__name__} with a primary value of {value}")

    @classmethod
    def by_name(cls, name: str):
        """
        Returns the element that matches the given `name`. You could simply refer
        to `TheEnum[name]`, but that raises an exception if not found, while this
        method return `None`. But first, it'll try again looking for the name in
        all lower-case (casefold), and again in all uppercase.
        """
        return enum_by_name(cls, name)

    @classmethod
    def default(cls):
        """
        Returns the first member defined.

        NOTE: Override this method for anything more complicated.
        """
        # We can't just index it as `cls[0]` because __getitem__ looks for the
        # member name, not the position.
        for e in cls:
            return e


# ############################################################################
#                                                         STANDALONE FUNCTIONS
# ############################################################################

def enum_default_value(enum_class):
    """
    Returns an appropriate default value for the given Enum class. If the Enum
    has a `default()` method, than we call that; otherwise, we return the first
    member defined in the Enum.

    :param enum_class: The enum type (class).
    :return: The default member for that enum.
    """
    if hasattr(enum_class, 'default'):
        return enum_class.default()
    for e in enum_class:
        return e
    return None


def enum_by_name(enum_class, name: str):
    """
    Returns the element that matches the given `name`. You could simply refer
    to `TheEnum[name]`, but that raises an exception if not found, while this
    method returns `None`. But first, it'll try again looking for the name in
    all lower-case (casefold), and again in all uppercase.
    """
    # IMPORTANT: Any chnges to this function MUST be copied over to the
    # `kivygw` package.
    # FIXME Automate this with some sort of an INCLUDE directive

    if name is None:
        return None
    if not isinstance(name, str):
        return None
    name = name.strip()
    with contextlib.suppress(KeyError):
        return enum_class[name]
    with contextlib.suppress(KeyError):
        return enum_class[name.casefold()]
    with contextlib.suppress(KeyError):
        return enum_class[name.upper()]
    return None

