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
from typing import Dict, List, Optional, Tuple

from .gw_colors import NamedColor
from .gw_exceptions import GruntWurkConfigError
from collections import namedtuple

LOG = logging.getLogger("main")

Color = Optional[Tuple[int, int, int]]

class GlobalSettings(SimpleNamespace):
    """
    A singleton namespace to hold an application's configuration settings.
    """
    __instances = {}

    def __new__(cls, group:str="config", **kwargs):
        if  group not in GlobalSettings.__instances:
            GlobalSettings.__instances[group] = SimpleNamespace.__new__(cls, group, **kwargs)
        return GlobalSettings.__instances[group]

    def __init__(self, group, initial_settings: SimpleNamespace = None):
        self.group = group
        if initial_settings:
            self.update(initial_settings)

    def __del__(self):
        del GlobalSettings.__instances[self.group]

    def update(self, other: SimpleNamespace):
        self.__dict__.update(other.__dict__)

    def get(self, key):
        if key not in self.__dict__:
            LOG.warning(f"Configuration setting '{key}' does not exist. Initializing it to None.")
            self.__dict__[key] = None
        return self.__dict__[key]

    def sorted_keys(self) -> List[str]:
        sorted = []
        sorted.extend(self.__dict__.keys())
        sorted.sort()
        return sorted



def as_path(input: any) -> Path:
    """This can be used to extend ConfigParser to understand Path types."""
    p = input if isinstance(input, Path) else None
    if isinstance(input, str):
        p = Path(input)
    if p:
        p = p.expanduser()
    return p


def as_color(input: any) -> Color:
    """
    This can be used to extend ConfigParser to understand colors,
    returning a tuple with the NamedColor values.
    A color (as configured) can be represented in hex format (#ff0088) or a
    tuple (255,0,136). Parens are optional.
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
    This can be used to extend ConfigParser to understand colors, returning one
    of 550 enumerated colors (an instance of the NamedColor class).
    A color (as configured) can be represented in hex format (#ff0088),
    a tuple (255,0,136), or the name (e.g. SKYBLUE4).
    Everything is case insensitive.
    The leading # is optional for hex format.
    The parens are optional for NamedColor tuples.
    If name is given that doesn't exist (e.g. AZURE), it will look for a color
    of the same name but with a 1 suffix (e.g. AZURE1).
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


STANDARD_CONVERTERS = {
    "path": as_path,
    "color": as_color,
    "text": as_text,
}


class GWConfigParser(ConfigParser):
    """
    A subclass of ConfigParser with four additional converters:
        as_text (thus, it knows how to do .gettext())
        as_path (thus, it knows how to do .getpath())
        as_color (thus, it knows how to do .getcolor()).
        as_q_color (thus, it knows how to do .getqcolor()).
    """
    def __init__(self, configfile=None, converters: dict = {}, **kwds) -> None:
        converters.update(STANDARD_CONVERTERS)
        super().__init__(converters=converters, **kwds)
        if configfile:
            self.parse_file(configfile)

    def parse_file(self, configfile: Path, encoding="utf8"):
        try:
            with configfile.open("rt", encoding=encoding) as f:
                self.read_file(f)
        except Exception as e:
            LOG.exception(e)

    def section_as_dict(self, section) -> Dict[str, str]:
        """
        A quick and dirty way to get all of the contents of a single section
        (with all values as simple strings). Useful for previewing
        a config file to see if it's the right one, for example.
        """
        contents = {}
        if self.has_section(section):
            for option in self.items(section):
                contents[option] = self[section].gettext(option)
        return contents




def parse_config(
    log: logging.Logger,
    configfile: Optional[Path] = None,
    ini: str = "",
    parser: ConfigParser = None,
    encoding="utf8",
) -> ConfigParser:
    """
    DEPRECATED: Instaniates a ConfigParser and loads it with the contents of the named file, or the text of the ini argument (whichever is given).
    (If both are given, the direct INI text takes prcedence.)
    You can pass in your own ConfigParser to use, otherwise a straight-forward instance
    will be used.
    """
    parser = GWConfigParser()
    if ini:
        parser.read_string(ini)
    elif configfile and configfile.is_file():
        parser.parse_file(configfile, encoding)
    return parser


__all__ = ["GlobalSettings", "GWConfigParser", "parse_config", "as_path", "as_text", "as_color", "as_named_color"]
