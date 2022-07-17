"""
CONFIG FILE (INI) SUPPORT

Helpers for working with config files via ConfigParser (INI format).

* GWConfigParser is a subclass of ConfigParser that adds type conversions for Path, Color (tuple), QColor, and text.
* It also adds a .section_as_dict() method.
* It includes specific handling for "theme" configurations.
"""
import re
import logging
from configparser import ConfigParser
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple, Union

from gwpycore.gw_basis.gw_typing import Singleton

from .gw_colors import NamedColor

Color = Optional[Tuple[int, int, int]]

MAIN_LOGGER_KEY = "main_logger"  # TODO is there a better name for this? or a better way?


@Singleton
class GlobalSettings(SimpleNamespace):
    """
    A singleton namespace to hold an application's configuration settings.
    Simply use `CONFIG = GlobalSettings()` to access the settings from
    anywhere within the application.

    This version of SimpleNamespace also has some extra features:

    * If you have a setting called `loglevel`, for example, and you try
      to access it as `CONFIG.log_level` (with an underscore) it'll find
      it anyway.
    * If a requested setting does not already exist, it will automatically
      be created (initialized to None) -- as opposed to raising an exception.
      It does log a warning, though.

    TIP: Use the `.update()` method to import the values of an existing
    namespace into this one. (e.g. an instance of `argparse.Namespace`).
    """
    def update(self, other: SimpleNamespace):
        """
        Imports the values of another namespace into this one.

        :param other: Another Namespace (e.g. an instance of
        `argparse.Namespace` from which to initialize/enhance the set of
        values for this Namespace.
        """
        self.__dict__.update(other.__dict__)

    def get(self, key):
        if key not in self.__dict__:
            if "_" in key:
                alt_key = key.replace("_", "")
                if alt_key in self.__dict__:
                    key = alt_key
                else:
                    self.logger().warning(f"Configuration setting '{key}' does not exist. Initializing it to None.")
                    self.__dict__[key] = None
        return self.__dict__[key]

    def logger(self):
        log_name = self.get(MAIN_LOGGER_KEY)
        log_name = log_name + ".gruntwurk" if log_name else "gruntwurk"
        return logging.getLogger(log_name)

    def sorted_keys(self) -> List[str]:
        sorted = []
        sorted.extend(self.__dict__.keys())
        sorted.sort()
        return sorted


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
    text = None
    if isinstance(input, str):
        text = input
    return text


GW_STANDARD_CONVERTERS = {
    "path": as_path,
    "color": as_color,
    "namedcolor": as_named_color,
    "text": as_text,
}


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
    def __init__(self, configfile=None, converters: dict = {}, **kwds) -> None:
        converters.update(GW_STANDARD_CONVERTERS)
        super().__init__(converters=converters, **kwds)
        if configfile:
            self.parse_file(configfile)

    def parse_file(self, configfile: Union[Path, str], encoding="utf8"):
        with Path(configfile).open("rt", encoding=encoding) as f:
            self.read_file(f)

    def section_as_dict(self, section) -> Dict[str, str]:
        """
        A quick way to get all of the contents of a single section (with all
        values as simple strings). Useful for previewing a config file to see
        if it's the right one, for example.
        """
        contents = {}
        if self.has_section(section):
            for option in self.items(section):
                contents[option] = self[section].gettext(option)
        return contents


__all__ = [
    "GlobalSettings",
    "GWConfigParser",
    "as_path", "as_text", "as_color", "as_named_color"
]
