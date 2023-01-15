"""
Tools for loading individual .kv files (one per screen).

NOTE: See also widgets/screen_widget.py
"""
import importlib
import logging

from pathlib import Path
from kivy.uix.screenmanager import Screen, ScreenManager, ScreenManagerException
from kivy.lang import Builder
from kivy.app import App

from gwpycore import snake_case, package_name, GWFileNotFoundError

LOG = logging.getLogger("gwpy")

__all__ = [
    "load_kv",
    "load_screen",
    "switch_to_screen",
]


_previous_screen = ''


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

    LOG.diagnostic(f"Loading class {class_name}, from module {pkg_name}, in {pkg_path}")
    screen_name = snake_case(class_name)
    kv_file = Path(pkg_path) / f"{screen_name}.kv"
    if not kv_file.exists():
        kv_file = Path(alternate_path) / f"{screen_name}.kv"
    if kv_file.exists():
        Builder.load_file(str(kv_file))
        LOG.debug(f"KV file loaded: {kv_file}")
    elif kv_file_required:
        raise GWFileNotFoundError(f"Cannot locate KV file: {kv_file}")
    return screen_name


def load_screen(manager: ScreenManager, class_ref) -> object:
    """
    Loads a "screen" class and its corresponding `.kv` file.

    :param class_ref: A reference to the class to load.
    """
    # app: App = App.get_running_app()
    screen_name = load_kv(class_ref, kv_file_required=True)
    screen_obj = class_ref(name=screen_name)
    manager.add_widget(screen_obj)
    LOG.debug(f"{screen_obj.__class__.__name__} instantiated with name: {screen_name}")
    return screen_obj


def switch_to_screen(screen_name='') -> Screen:
    global _previous_screen
    app: App = App.get_running_app()
    manager: ScreenManager = app.root
    if not screen_name:
        screen_name = _previous_screen
    else:
        _previous_screen = manager.current
    try:
        manager.current = screen_name
    except ScreenManagerException:
        LOG.error(f"No such screen as {screen_name}. Choices are: {manager.screen_names}.")
    return manager.current_screen


