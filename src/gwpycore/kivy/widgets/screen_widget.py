import logging
import importlib
from pathlib import Path

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, ScreenManagerException
from kivy.lang import Builder

from ...core.strings import snake_case
from ...core.typing_utils import package_name
from ...core.exceptions import GWFileNotFoundError

LOG = logging.getLogger("gwpy")


__all__ = [
    "load_kv_for_class",
    "GWScreen",
]


def load_kv_for_class(cls, kv_file_required=True, alternate_path="assets") -> str:
    """
    Locates a corresponding `.kv` file for this class and loads it.
    (By convention, the App's build() method looks for `badgemaker.kv` (the
    app's class name minus the "App") and loads it. But we prefer to have a
    separate `.kv` file for each screen.)

    :param kv_file_required: Whether or not to raise an exception if there is
    no corresponding KV file. Default is True.

    :param alternate_path: A second place to look for the `.kv` file (if not found
    alongside the `.py` file). For example, a deployment via `pyinstaller` might
    place the `.kv` files in the `assets` folder. Default is `assets`.

    :returns: The name of the screen (snake case).
    """
    class_name = cls.__name__
    id = snake_case(class_name)
    pkg_name = package_name(cls.__module__)
    LOG.debug(f"class_name = {id}, pkg_name = {pkg_name}")
    # The package's __file__ is the __init__.py
    kv_file = Path(importlib.import_module(pkg_name).__file__).parent / f"{id}.kv"

    LOG.diagnostic("Loading class {}, from module {}, in {}".format(class_name, pkg_name, kv_file))
    if not kv_file.exists():
        kv_file = Path(alternate_path) / kv_file.name
    if kv_file.exists():
        Builder.load_file(str(kv_file))
        LOG.debug("KV file loaded: {}".format(kv_file))
    else:
        if kv_file_required:
            raise GWFileNotFoundError("Cannot locate KV file: {}".format(kv_file))
    return id


class GWScreen(Screen):
    _previous_screen_stack = []

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = None
        # self.name is needed for when we add this instance to the ScreenManager
        self.name = snake_case(self.__class__.__name__)

    @classmethod
    def classname_snake(cls):
        return snake_case(cls.__name__)

    @classmethod
    def load_kv(cls, kv_file_required=True, alternate_path="assets") -> str:
        return load_kv_for_class(cls, kv_file_required=kv_file_required, alternate_path=alternate_path)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.app = App.get_running_app()

    def cancel(self):
        self.close()

    def close(self):
        GWScreen.switch_to_screen()  # pop to previous screen

    @classmethod
    def screen_manager(cls) -> ScreenManager:
        return App.get_running_app().root

    @classmethod
    def switch_to_screen(cls, screen_name='') -> Screen:
        mgr = cls.screen_manager()
        if not screen_name:
            if len(GWScreen._previous_screen_stack) <= 0:
                cls.switch_to_screen('main_screen')
            screen_name = cls._previous_screen_stack.pop()
        else:
            cls._previous_screen_stack.append(mgr.current)
        try:
            mgr.current = screen_name
        except ScreenManagerException:
            LOG.error(f"No such screen as {screen_name}. Choices are: {mgr.screen_names}.")
        return mgr.current_screen

