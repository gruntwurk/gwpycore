from typing import List


def bump_version(current_version: str) -> str:
    """
    Returns the given string with a 3-part version number with the third part incremented.
    """
    numeric = version_numeric(current_version)
    numeric[2] += 1
    return ".".join([str(v) for v in numeric])


def version_numeric(version: str) -> List[int]:
    """
    Converts a version number string (dot-seperated) to an int array.
    """
    return [int(v) for v in version.split(".")]


__all__ = ("bump_version", "version_numeric")
