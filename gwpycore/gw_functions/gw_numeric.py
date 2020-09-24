def next_in_range(index, increment, max_value) -> int:
    index += increment
    if index >= max_value:
        index = 0
    if index < 0:
        index = max_value
    return index

__all__ = "next_in_range"