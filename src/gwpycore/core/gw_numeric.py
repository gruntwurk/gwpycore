def next_in_range(index, max_value, min_value=0, increment=1) -> int:
    """
    Increments an index while keeping it in range.
    """

    index += increment
    if index > max_value:
        index = min_value
    if index < min_value:
        index = max_value
    return index


__all__ = [
    "next_in_range",
]
