import contextlib
from enum import Enum
from typing import List

from gwpycore.core.strings import normalize_name

from .exceptions import GWValueError

__all__ = [
    'GWEnum',
    'enum_default_value',
    'enum_by_value',
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
        * (class) `by_name` -> (enum element)
        * (class) `by_value`, -> (enum element)
        * (class) `default` -> (enum element)
    """

    def display_name(self) -> str:
        """
        How to describe this element to the user (e.g. as a choice in a dropdown
        (spinner) widget.

        :return: The primary value, if it's a string; otherwise, the element name.
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
        Returns the first element defined.

        NOTE: Override this method for anything more complicated.
        """
        # We can't just index it as `cls[0]` because __getitem__ looks for the
        # element name, not the position.
        for e in cls:
            return e


# ############################################################################
#                                                         STANDALONE FUNCTIONS
# ############################################################################

def enum_default_value(enum_class):
    """
    Returns an appropriate default value for the given Enum class. If the Enum
    has a `default()` method, than we call that; otherwise, we return the first
    element defined in the Enum.

    :param enum_class: The enum type (class). Any subclass of Enum.

    :return: The default element for that enum.
    """
    if hasattr(enum_class, 'default'):
        return enum_class.default()

    # FIXME
    # We can't just return enum_class[0] because the get dunder goes by name,
    # not the position index.
    for e in enum_class:
        return e  # The first one, whatever it is.
    return None


def enum_by_value(enum_class, value: str):
    """
    Returns the element of `enum_class` that best matches the given `value`.
    In order for this to work, the element's value either needs to be a
    simple string, or else the class must have at least one of the following
    methods defined:

    `by_value()` -- (class method) that knows how to find the right element.
    `description()` -- extracts the description str from the complex enum value.
    `primary_value()` -- extracts the main value from the complex enum value
        which either needs to be a str, or can be converted to one via `str()`.

    Failing all of that, we punt over to `enum_by_name()` in case they
    actually passed in the name rather than the value.

    :param enum_class: The enum type (class). Any subclass of Enum.

    :param value: The value (or name) of the enum to fetch.

    :return: The identified enum element, or None.
    """
    if not value or not isinstance(value, str):
        return None

    # sourcery skip: assign-if-exp, reintroduce-else
    if hasattr(enum_class, 'by_value'):
        if e := enum_class.by_value(value):
            return e

    if hasattr(enum_class, 'description'):
        for e in enum_class:
            if e.description() == value:
                return e

    if hasattr(enum_class, 'primary_value'):
        for e in enum_class:
            if str(e.primary_value()) == value:
                return e

    for e in enum_class:
        if e.value() == value:
            return e

    # Last resort, maybe the given value is actually the element name
    return enum_by_name(enum_class, value)


def enum_by_name(enum_class, name: str):
    """
    Returns the element of `enum_class` that best matches the given `name`.
    First, the name is normalized to exclude anything other than alphanumerics
    and underscores, since all Enum element names conform to Python identifier
    rules. Then, it tries to find any variation of the name from as-is, to
    lower case, to upper case.
    NOTE: `GWEnum.by_name` calls this function, not the other way around.

    :param enum_class: The enum type (class). Any subclass of Enum.

    :param name: The name of the enum to fetch.

    :return: The identified enum element, or None.
    """
    if name is None or not isinstance(name, str):
        return None

    name = normalize_name(name.strip(), '')
    if not name:
        return None
    with contextlib.suppress(KeyError):
        return enum_class[name]
    with contextlib.suppress(KeyError):
        return enum_class[name.casefold()]
    with contextlib.suppress(KeyError):
        return enum_class[name.upper()]
    return None
