"""
Helpers for working with config files via ConfigParser (INI format)
"""
import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from .gw_exceptions import GruntWurkConfigError


def as_path(input: any) -> Path:
    """This can be used to extend ConfigParser to understand Path types."""
    p = input if isinstance(input, Path) else None
    if isinstance(input, str):
        p = Path(input)
    if (p):
        p = p.expanduser()
    return p

ADDITIONAL_CONVERTERS = {"path": as_path}


def parse_config(log: logging.Logger, configfile: Optional[Path], parser: ConfigParser = None) -> ConfigParser:
    """
    Instaniates a ConfigParser and loads it with the contents of the named file.
    Any errors are captured and logged, but does not prevent the code from continuing.
    You can pass in your own ConfigParser to use, otherwise a straight-forward instance
    will be used (with just one additional converter: asPath).
    """
    if not parser:
        parser = ConfigParser(converters=ADDITIONAL_CONVERTERS)
    else:
        parser.converters.append(ADDITIONAL_CONVERTERS)

    if configfile and configfile.is_file():
        log.trace("Loading configuration file {configfile}")
        try:
            with configfile.open("rt") as f:
                parser.read_file(f)
        except GruntWurkConfigError as e:
            log.exception(e)
    return parser


__all__ = ("parse_config","as_path")
