def as_bool(input: any) -> bool:
    """
    Converts a string to a Boolean. Understands: yes/no, y/n, 1/0, true/false,
    t/f (case insensitive). Anything else is considered False.
    This can be used to extend `ConfigParser` to understand yes/no types.
    This is also useful for importing data from a text file (csv, tsv, fixed format, etc.)
    """
    if type(input) == str:
        return input.casefold() in ['1', 'true', 't', 'yes', 'y']
    return bool(input)


