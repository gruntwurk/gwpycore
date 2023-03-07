import contextlib

__all__ = [
    'enum_default_value',
    'enum_by_name',
]


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
    name = name.strip()
    with contextlib.suppress(KeyError):
        return enum_class[name]
    with contextlib.suppress(KeyError):
        return enum_class[name.casefold()]
    with contextlib.suppress(KeyError):
        return enum_class[name.upper()]
    return None
