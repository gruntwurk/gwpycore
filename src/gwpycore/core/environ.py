import sys, os
from importlib.util import find_spec
from sys import platform

__all__ = [
    "machine_id",
    "is_windows",
    "is_module_installed"
]


def machine_id():
	return os.environ["COMPUTERNAME"]


def is_windows() -> bool:
    return platform == "win32"


def is_module_installed(module_name: str) -> bool:
    if module_name in sys.modules:
        return True
    return find_spec(module_name) is not None

