import contextlib

__all__ = [
    'enum_by_name',
]


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
