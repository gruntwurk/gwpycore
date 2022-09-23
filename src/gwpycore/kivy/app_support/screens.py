"""
Tools for loading individual .kv files (one per screen).
"""
import importlib
import logging

from pathlib import Path
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from gwpycore import snake_case, package_name, GWConfigError

LOG = logging.getLogger("gwpy")

def load_kv(class_ref, kv_file_required=True, alternate_path="assets") -> str:
    """
    Given a reference to a user-defined widget class, this looks for a
    corresponding `.kv` file and loads it.

    :param class_ref: A reference to the class to load.

    :param kv_file_required: Whether or not to raise an exception if there is
    no corresponding KV file. Default is True.

    :param alternate_path: A second place to look for the `.kv` file (if not found
    alongside the `.py` file). For example, a deployment via `pyinstaller` might
    place the `.kv` files in the `assets` folder. Default is `assets`.

    :returns: The name of the screen (snake case).
    """

    class_name = class_ref.__name__
    pkg_name = package_name(class_ref.__module__)
    # LOG.debug("class_name = {}".format(class_name))
    # LOG.debug("pkg_name = {}".format(pkg_name))
    pkg_path = Path(importlib.import_module(pkg_name).__file__).parent

    LOG.diagnostic("Loading class {}, from module {}, in {}".format(class_name, pkg_name, pkg_path))
    id = snake_case(class_name)
    kv_file = Path(pkg_path) / f"{id}.kv"
    if not kv_file.exists():
        kv_file = Path(alternate_path) / f"{id}.kv"
    if kv_file.exists():
        Builder.load_file(str(kv_file))
        LOG.debug("KV file loaded: {}".format(kv_file))
    else:
        if kv_file_required:
            raise GWConfigError("Cannot locate KV file: {}".format(kv_file))
    return id

def load_screen(manager: ScreenManager, class_ref) -> object:
    """
    Loads a "screen" class and its corresponding `.kv` file.

    :param class_ref: A reference to the class to load.
    """
    screen_name = load_kv(class_ref, kv_file_required=True)
    screen_obj = class_ref(name=screen_name)
    manager.add_widget(screen_obj)
    LOG.debug("{} instantiated with name: {}".format(screen_obj.__class__.__name__, screen_name))
    return screen_obj


__all__ = [
    "load_kv",
    "load_screen",
]