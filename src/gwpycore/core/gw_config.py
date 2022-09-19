"""
CONFIG FILE (INI) SUPPORT

Helpers for working with config files via ConfigParser (INI format).

* GWConfigParser is a subclass of ConfigParser that adds type conversions for Path, Color (tuple), QColor, and text.
* It also adds a .section_as_dict() method.
* It includes specific handling for "theme" configurations.
"""
import logging
import re
from configparser import ConfigParser
from pathlib import Path
from itertools import chain
from typing import Dict, List, Optional, Tuple, Union

from .gw_exceptions import GWConfigError, GWWarning
from .gw_typing import Singleton
from .gw_colors import NamedColor, color_parse
from .gw_strings import normalize_name

LOG = logging.getLogger("gwpy")

Color = Optional[Tuple[int, int, int]]

_RAISE_KEY_ERROR = object()  # singleton for no-default behavior (can't use None here, because None is valid default value)


def as_bool(input: any) -> bool:
    if type(input) == str:
        return input.casefold() in ['1', 'true', 't', 'yes', 'y']
    return bool(input)


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
    RGB tuples. Either a 3-tuple or a 4-tuple will be returned, depending on
    the input.

    A color (as configured) can be represented in hex format e.g. #ff0088 or
    #ff008840, or a tuple e.g. (255,0,136) or (255,0,136,40), or the color
    name (e.g. SKYBLUE4) accordibng to our `NamedColor` enum (550 enumerated
    colors). The leading number-sign (#) is optional for hex format. Parens
    are optional for RGB tuples. All settings are case-insensitive.

    NOTE: The only difference between `as_color` as `as_named_color` is what
    type of value is returned. Both accept the same variety of inputs.
    """
    return color_parse(input)


def as_named_color(input: any) -> NamedColor:
    """
    This can be used to extend `ConfigParser` to understand colors in terms of
    our `NamedColor` enum (i.e. one of 550 enumerated colors). Be aware, if
    the input includes an alpha channel (a fourth value), it will be ignored
    when converted to a NamedColor.

    A color (as configured) can be represented in hex format e.g. #ff0088 or
    #ff008840, or a tuple e.g. (255,0,136) or (255,0,136,40), or the color
    name (e.g. SKYBLUE4) accordibng to our `NamedColor` enum (550 enumerated
    colors). The leading number-sign (#) is optional for hex format. Parens
    are optional for RGB tuples. All settings are case-insensitive.

    NOTE: The only difference between `as_color` as `as_named_color` is what
    type of value is returned. Both accept the same variety of inputs.
    """
    return NamedColor.by_value(color_parse(input))



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


# ############################################################################
#                                                                       GWDict
# ############################################################################

class GWDict(dict):
    """
    An enhanced dictionary/namespace. Used, for example, as the base class for
    GlobalSettings() and GlobalState().

    * All settings can be accessed as attributes as well as indicies.
      So, `my_dict['foo'] = 'bar'` is the same as `my_dict.foo = 'bar'`.

    * Any key that contains spaces or dashes will always be normalized to
      use underscores instead, both when settings values and retrieving them, e.g.
      `my_dict["my lazy-setting"] = "foo"` will actually set
      `my_dict["my_lazy_setting"] = "foo"` and then
      `my_dict["my lazy-setting"]`, `my_dict["my_lazy_setting"]`, and
      `my_dict.my_lazy_setting` will all return that `"foo"`.

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

    # def __len__(self):
    #     return len(self.__dict__)

    def set_as_immutable(self, key, value):
        """
        Sets the given key/value pair (but only if the value is not None).
        The pair is also marked as being immutable (unchangeable) from now on.
        NOTE: If the key is already marked as immutable, then this does nothing.
        """
        if value is None:
            return
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
            for other_key in other:
                self.set_as_immutable(other_key, other[other_key])
        except TypeError:
            try:
                for other_key in other.__dict__:
                    self.set_as_immutable(other_key, other.__dict__[other_key])
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


# ############################################################################
#                                                              GLOBAL SETTINGS
# ############################################################################
@Singleton
class GlobalSettings(GWDict):
    """
    A singleton instance of GWDict (an enhanced dictionary) intended to hold
    an application's configuration settings.

    Simply use `CONFIG = GlobalSettings()` to access the settings from
    anywhere within the application.

    An `import_setting()` method makes it easy to import values from a
    `GWConfigParser` (or plain `ConfigParser`).
    """
    def import_setting(self, setting_names: Union[str, List], section: str = "",
                       default=None, include_section_name=False, how=None, config_parser=None):
        """
        Imports a single setting from the given config parser.

        TIP: If you explicitly set `CONFIG.config_parser` to your instance of
        `ConfigParser`, then you do not have to pass it in at all.

        :param setting_name: The name(s) of one or more setting(s) as they
        appear in the INI file. The corresponding dictionary keys are
        determined by normalizing these names to lower case and replacing
        all non-alphanumerics with undserscores.

        :param section: Section name within the INI file where the setting will
        be found. Defaults to "" (no section).

        :param default: The default value to use (in case the section doesn't
        exist, or the setting doesn't exist within the section). NOTE: If no
        default is supplied then nothing happens.

        :param include_section_name: Whether or not to prefix the dictionary
        key with the section name (separated by an underscore).

        :param how: Either the name of a converter that the config parser knows
        about, or a callback function for processing the value directly. The
        initial set of known converters are: `boolean`, `float`, `int`, `path`,
        `color`, `namedcolor`, and `text`. The default is `text`.

        :param config_parser: The config parser object from which to obtain the
        setting value. Default is the same config parser as the last time (i.e.
        whatever the current value of `CONFIG.config_parser` is).
        """
        LOG.trace("import_setting")
        if config_parser:
            self.config_parser = config_parser
        if not self.config_parser:
            raise GWConfigError("GlobalSettings: import_setting() requires a config parser to be specified (the first time).")

        if type(how) == str:
            how = self.config_parser.converter(how)
            LOG.debug("how = {}".format(how))
        if not how:
            how = lambda x: x  # noqa E731

        if type(setting_names) is str:
            setting_names = [setting_names]

        for setting_name in setting_names:
            key = normalize_name((section + '_' if include_section_name else "") + setting_name).casefold()
            if self.config_parser.has_section(section):
                value = self.config_parser[section].get(setting_name)
                if value is not None:
                    self[key] = how(value)
                elif default is not None:
                    self[key] = default
            elif default is not None:
                self[key] = default


# ############################################################################
#                                                                 GLOBAL STATE
# ############################################################################
@Singleton
class GlobalState(GWDict):
    """
    A singleton instance of GWDict (an enhanced dictionary) intended to hold
    an application's persistent state (e.g. the window's position and size).

    Simply use `STATE = GlobalState()` to access the settings from anywhere
    within the application.

    Use `STATE.load(filename)` to read the contents of the state file (INI
    format) into the dict.

    Use `STATE.save()` to write the contents of the dictionary back out to
    the state file, overwriting the original file.

    """
    def load(self, state_file: Union[Path, str], encoding="utf8"):
        """
        Loads the contents of a file (pseudo INI file format). [section]
        headings are ignored, as are any lines that do not contain at least
        one equal sign (=).

        :param state_file: file name (str or Path)
        :param encoding: defaults to "utf8"
        :raises GWConfigError: If no file specified.
        :raises GWWarning: If the file does not exist.
        """
        self._state_file = Path(state_file)
        if not self._state_file:
            raise GWConfigError("No state file specified.")
        if not self._state_file.exists():
            raise GWWarning("State file {} does not exist. Initializing as empty.".format(str(self._state_file)))
        with self._state_file.open("rt", encoding=encoding) as f:
            self.load_lines(f.readlines())

    def load_lines(self, lines: List[str]):
        for line in lines:
            # ignore INI [headers]
            if re.match(r"^\[.*\] *$", line):
                continue
            if m := re.match(r"^([^=]+)=(.*)$", line):
                self[m.group(1)] = m.group(2)
            # ignore any lines without an =

    def save(self, heading="state"):
        """
        Writes (persists) the state information back out to the file (as
        specified by the last time the load() method was called).

        :param heading: _description_, defaults to "state"

        :raises GWConfigError: If no file specified. (load() must be called first.)
        :raises GWWarning: If the dictionary is empty.
        """
        if len(self) == 0:
            raise GWWarning("No state values to persist. Nothing written.")
        if not self._state_file:
            raise GWConfigError("No state file specified. load() must be called before save().")

        lines = [f"[{heading}]"]
        for name in self.keys():
            if not name.startswith("_"):
                lines.append(f"{name}={self[name]}")
        self._state_file.write_text("\n".join(lines))


# ############################################################################
#                                                             GW CONFIG PARSER
# ############################################################################

class GWConfigParser(ConfigParser):
    """
    A subclass of ConfigParser with four additional converters:

        * `as_text` (thus, it knows how to do `.gettext()` -- just a synonym for
            .get() but consistent naming with the other get methods)
        * `as_path` (thus, it knows how to do `.getpath()`)
        * `as_color` (thus, it knows how to do `.getcolor()`).
        * `as_named_color` (thus, it knows how to do `.getnamedcolor()`).

    Usage
    ~~~~
    global CONFIG
    CONFIG = GlobalSettings()  # singleton class

    # Optionally start with command-line arguments (via our enhanced
    # ArgParser, or however you prefer)
    arg_parser = basic_cli_parser(...)
    CONFIG.update(arg_parser.parse_args())

    # Now, create the ConfigParser
    config_parser = GWConfigParser(configfile="my-main.ini")
    config_parser.parse_file(configfile="my-secondary.ini")

    # Then, proceed to query the config_parser for settings brought in
    # from the INI file(s), typically transfering them into the global
    # CONFIG namespace, e.g.:

    if config_parser.has_section("display"):
        CONFIG.serif_typeface = config_parser["display"].gettext(
            "serif_typeface", CONFIG.serif_typeface)
        CONFIG.serif_color = config_parser["display"].getnamedcolor(
            "serif_color", CONFIG.serif_color)
    ~~~~
        )

    """
    def __init__(self, config_file=None, converters: dict = {}, **kwds) -> None:
        converters.update(GW_STANDARD_CONVERTERS)
        super().__init__(converters=converters, **kwds)
        if config_file:
            self.parse_file(config_file)

    def parse_file(self, config_file: Union[Path, str], encoding="utf8"):
        if not config_file:
            raise GWWarning("No config file specified. Using defaults.")
        path = Path(config_file)
        if not path.exists():
            raise GWWarning("Config file {} does not exist. Using defaults.".format(str(config_file)))
        with path.open("rt", encoding=encoding) as f:
            self.read_file(f)

    def section_as_dict(self, section) -> Dict[str, str]:
        """
        A quick way to get all of the contents of a single section (with all
        values as simple strings). Useful for previewing a config file to see
        if it's the right one, for example.
        """
        contents = {}
        if self.has_section(section):
            for setting_name, value in self.items(section):
                LOG.debug(f"{setting_name} = {value}")
                contents[setting_name] = value  # self[section].get(setting_name)
        return contents

    def available_converters(self) -> List[str]:
        converters = []
        for x in self._converters.keys():
            converters.append(x)
        return converters

    def converter(self, converter_name):
        converter_name = converter_name.replace('_', '')
        if converter_name == "int":
            return int
        elif converter_name == "float":
            return float
        elif converter_name == "bool":
            return as_bool
        elif converter_name in self.available_converters():
            return self._converters[converter_name]
        return None


__all__ = [
    "GWDict",
    "GlobalSettings",
    "GlobalState",
    "GWConfigParser",
    "as_path", "as_text", "as_color", "as_named_color"
]
