"""
CONFIG FILE (INI) SUPPORT

Helpers for working with config files via ConfigParser (INI format).

* GWConfigParser is a subclass of ConfigParser that adds type conversions for Path, Color (tuple), QColor, and text.
* It also adds a .section_as_dict() method.
* It includes specific handling for "theme" configurations.
"""
import re
from configparser import ConfigParser
from pathlib import Path
from itertools import chain
from typing import Dict, List, Optional, Tuple, Union

from .gw_exceptions import GWConfigError
from .gw_typing import Singleton
from .gw_colors import NamedColor
from .gw_strings import normalize_name

Color = Optional[Tuple[int, int, int]]

_RAISE_KEY_ERROR = object()  # singleton for no-default behavior (can't use None here, because None is valid default value)


def as_path(input: any) -> Path:
    """This can be used to extend `ConfigParser` to understand `pathlib.Path` types."""
    p = input if isinstance(input, Path) else None
    if isinstance(input, str):
        p = Path(input)
    if p:
        p = p.expanduser()
    return p


def as_color(input: any) -> Color:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    RGB tuples. A color (as configured) can be represented in hex format
    (#ff0088) or a tuple (255,0,136). The leading # is optional for hex format.
    Parens are optional for RGB tuples.
    """
    color = input if isinstance(input, Tuple) else None
    if isinstance(input, str):
        # remove irrelevant chars
        input = re.sub(r"[^#0-9a-fA-F,]", "", input)

        if re.match(r"#[0-9a-fA-F]{6}", input):
            color = tuple(bytes.fromhex(input[1:]))
        else:
            parts = input.split(",")
            if len(parts) == 3:
                color = tuple([int(x) for x in parts])
    return color


def as_named_color(input: any) -> NamedColor:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    our `NamedColor` enum (i.e. one of 550 enumerated colors). A color (as
    configured) can be represented in hex format (#ff0088), a tuple (255,0,136),
    or the name (e.g. SKYBLUE4). Everything is case insensitive. The leading #
    is optional for hex format. The parens are optional for RGB tuples.
    """
    if isinstance(input, Tuple):
        return NamedColor.by_value(input)

    if isinstance(input, str):
        # remove irrelevant chars
        input = re.sub(r"[^#0-9a-zA-Z,]", "", input)
        # First, try by name
        color = NamedColor.by_name(input)
        if color:
            return color

        m = re.match(r"#?([0-9a-fA-F]{6})", input)
        if m:
            return NamedColor.by_value(tuple(bytes.fromhex(m.group(1))))

        parts = input.split(",")
        if len(parts) == 3:
            return NamedColor.by_value((int(parts[0]),int(parts[1]),int(parts[2])))

    return None


def as_text(input: any) -> Optional[str]:
    """
    This is the same as a plain get(), but conforms to the signature as all of the other getters.
    """
    return str(input)


GW_STANDARD_CONVERTERS = {
    "path": as_path,
    "color": as_color,
    "namedcolor": as_named_color,
    "text": as_text,
}


@Singleton
class GlobalSettings(dict):
    """
    A singleton dictionary to hold an application's configuration settings.
    Simply use `CONFIG = GlobalSettings()` to access the settings from
    anywhere within the application.

    This subclass of dict also has some extra features:

    * All settings can be accessed as attribute as well as indicies.
      So, `CONFIG['foo'] = 'bar'` is the same as `CONFIG.foo = 'bar'`.

    * Any key that contains spaces or dashes will always be normalized to
      use underscores instead, both when settings values and retrieving them, e.g.
      `CONFIG["my lazy-setting"] = "foo"` will actually set
      `CONFIG["my_lazy_setting"] = "foo"` and then
      `CONFIG["my lazy-setting"]`, `CONFIG["my_lazy_setting"]`, and
      `CONFIG.my_lazy_setting` will all return that `"foo"`.

    * If a requested setting does not already exist, it will automatically
      be created (initialized to None) -- as opposed to raising an exception.

    * Immutables are supported. Any values that are set via either the
      `set_as_immutable()` method or the `update_as_immutable()` method will
      be "locked in." Any attempt to change any of those particular values
      will simply be ignored. One use-case for this is when command-line
      switches need to take precedence over any config-file settings, but the
      command-line switches are loaded before the config file.

    TIP: Use the `.update()` method to import the values of an existing
    namespace into this one. (e.g. an instance of `argparse.Namespace`).
    """
    __immutables__ = set()

    def _process_args(self, mapping=(), **kwargs):
        if hasattr(mapping, "items"):
            mapping = getattr(mapping, "items")()
        return ((self._key_transform(k), v) for k, v in chain(mapping, getattr(kwargs, "items")()))

    def __init__(self, mapping=(), **kwargs):
        super().__init__(self._process_args(mapping, **kwargs))

    def _key_transform(self, key):
        if not isinstance(key, (str, bytes, bytearray)):
            return key
        return re.sub(r'[- ]+', '_', key)

    def __missing__(self, key):
        super().__setitem__(key, None)
        return None

    def __getitem__(self, key):
        key = self._key_transform(key)
        return super().__getitem__(key)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        key = self._key_transform(key)
        if key not in self.__immutables__:
            super().__setitem__(key, value)

    def __setattr__(self, key, value):
        key = self._key_transform(key)
        if key not in self.__immutables__:
            super().__setitem__(key, value)

    def __delitem__(self, k):
        return super().__delitem__(self._key_transform(k))

    def get(self, k, default=None):
        return super().get(self._key_transform(k), default)

    def setdefault(self, k, default=None):
        return super().setdefault(self._key_transform(k), default)

    def pop(self, k, v=_RAISE_KEY_ERROR):
        if v is _RAISE_KEY_ERROR:
            return super().pop(self._key_transform(k))
        return super().pop(self._key_transform(k), v)

    def update(self, mapping=(), **kwargs):
        super().update(self._process_args(mapping, **kwargs))

    def __contains__(self, k):
        return super().__contains__(self._key_transform(k))

    def copy(self):  # don't delegate w/ super - dict.copy() -> dict :(
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, v=None):
        return super(GlobalSettings, cls).fromkeys((cls._key_transform(k) for k in keys), v)

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super().__repr__())

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def set_as_immutable(self, key, value):
        """
        Sets the given key/value pair, and also marks it as being immutable
        (unchangeable) from now on. NOTE: If the key is already marked as
        immutable, then this does nothing.
        """
        self[self._key_transform(key)] = value
        self.__immutables__.add(key)

    def update_as_immutable(self, other):
        """
        Imports the values of another dict-like object into this one. Also
        marks the imported keys as being immutable (unchangeable) from now on.

        :param other: Another Namespace (or anything dict-like) from which to
        initialize/enhance the set of values for this Namespace.
        """
        try:
            super().update(other)
            self.__immutables__.update(other)
        except TypeError:
            try:
                super().update(other.__dict__)
                self.__immutables__.update(other.__dict__)
            except TypeError:
                raise GWConfigError('GlobalSettings: Unable to update settings from a non-iterable dictionary source source.')

    def sorted_keys(self) -> List[str]:
        """
        Returns a sorted list of the keys.
        """
        sorted = []
        sorted.extend(self.keys())
        sorted.sort()
        return sorted

    def dump(self) -> List[str]:
        all = []
        for setting_name in self.keys():
            all.append("{} = {}".format(setting_name, self[setting_name]))
        return all

    def import_setting(self, setting_name: str, section: str = "", default=None, how=None, config_parser=None):
        """
        Imports a single setting from the given config parser.

        :param setting_name: Name of the setting as it appears in the INI file
        -- and also how it will be stored in this dictionary.

        :param section: Section name within the INI file where the setting will
        be found. Defaults to "" (no section).

        :param default: The default value to use (in case the section doesn't
        exist, or the setting doesn't exist within the section).

        :param how: Either the name of a converter that the config parser knows
        about, or a callback function for processing the value directly. The
        initial set of known converters are: `boolean`, `float`, `int`, `path`,
        `color`, `namedcolor`, and `text`. The default is `text`.

        :param config_parser: The config parser object from which to obtain the
        setting value. Default is the same config parser as the last time.
        """
        if config_parser:
            self.config_parser = config_parser
        if not self.config_parser:
            raise GWConfigError("GlobalSettings: import_setting() requires a config parser to be specified (the first time).")
        if type(how) == str:
            how = self.config_parser.converter(how)
        if not how:
            how = lambda x: x  # noqa E731
        if self.config_parser.has_section(section):
            self[setting_name] = how(self.config_parser[section].get(
                setting_name, default))
        else:
            self[setting_name] = default


class GWConfigParser(ConfigParser):
    """
    A subclass of ConfigParser with four additional converters:

        `as_text` (thus, it knows how to do `.gettext()` -- just a synonym for
            .get() but consistent naming with the other get methods)
        `as_path` (thus, it knows how to do `.getpath()`)
        `as_color` (thus, it knows how to do `.getcolor()`).
        `as_named_color` (thus, it knows how to do `.getnamedcolor()`).

    :usage:
        `global CONFIG`
        `CONFIG = GlobalSettings()`  # singleton class

        # Optionally start with command-line arguments (via our enhanced
        # ArgParser, or however you prefer)
        `arg_parser = basic_cli_parser(...)`
        `CONFIG.update(arg_parser.parse_args())`

        # Now, create the ConfigParser
        `config_parser = GWConfigParser(configfile="my-main.ini")`
        `config_parser.parse_file(configfile="my-secondary.ini")`

        Then, proceed to query the `config_parser` for settings brought in
        from the INI file(s), typically transfering them into the global
        CONFIG namespace, e.g.:

        `if config_parser.has_section("display"):`
        `    CONFIG.serif_typeface = config_parser["display"].gettext(`
        `        "serif_typeface", CONFIG.serif_typeface)`
        `    CONFIG.serif_color = config_parser["display"].getnamedcolor(`
        `        "serif_color", CONFIG.serif_color)`
        )

    """
    def __init__(self, config_file=None, converters: dict = {}, **kwds) -> None:
        converters.update(GW_STANDARD_CONVERTERS)
        super().__init__(converters=converters, **kwds)
        if config_file:
            self.parse_file(config_file)

    def parse_file(self, config_file: Union[Path, str], encoding="utf8") -> bool:
        path = Path(config_file)
        if path.exists():
            with path.open("rt", encoding=encoding) as f:
                self.read_file(f)
            return True
        return False

    def section_as_dict(self, section) -> Dict[str, str]:
        """
        A quick way to get all of the contents of a single section (with all
        values as simple strings). Useful for previewing a config file to see
        if it's the right one, for example.
        """
        contents = {}
        if self.has_section(section):
            for setting_name in self.items(section):
                contents[setting_name] = self[section].gettext(setting_name)
        return contents

    def converter(self, converter_name):
        converter_name = converter_name.replace('_', '')
        # for key in self._converters:
        #     print(key)
        if converter_name in self._converters:
            return self._converters[converter_name]
        return None


__all__ = [
    "GlobalSettings",
    "GWConfigParser",
    "as_path", "as_text", "as_color", "as_named_color"
]
