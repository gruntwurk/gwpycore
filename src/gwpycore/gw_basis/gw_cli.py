"""
Command Line Interface support. Helpers for working with argparse.ArgumentParser.
"""
from argparse import ArgumentParser

from .gw_logging import DEBUG, DIAGNOSTIC, INFO, TRACE


def basic_cli_parser(version_text="", command=False, verbose=True, very_verbose=True,
                     nocolor=True, filenames=None, devel=False, trace=False, configfile=False,
                     configfile_default="", logfile=False, logfile_default="", infile=False,
                     outfile=False, recurse=False) -> ArgumentParser:
    """
    Instantiates an `argparse.ArgumentParser` with a selection of commonly
    used switches.

    :param version_text: What to display if the `--version` switch is given.
    Defaults to nothing.

    :param command: Use `True` if you allow/require a command to appear on the
    line i.e. an argument without a leading dash. (Technically, it's a sub-
    command, with the program itself being the main command.) If so, the
    sub-command may appear before or after any switches. Accessed as
    `CONFIG.command`. (See note, below.)

    :param verbose: Whether or not to include a `-v` (`--verbose`) option.
    Defaults to True. Accessed as `CONFIG.loglevel` (set to `INFO`).

    :param very_verbose: Whether or not to include a `-vv` (`--very-verbose`)
    option. Defaults to True. Accessed as `CONFIG.loglevel` (set to `DEBUG`).

    :param nocolor: Whether or not to include a `--nocolor` option. Defaults to
    True. Accessed as `CONFIG.nocolor` (True/False).

    :param filenames: Whether or not you expect any filenames to be listed on
    the command line, and if so, how many (`filenames=3`, `filenames="*"`,
    `filenames="+"`, `filenames="?"`) `--` meaning: a specific number, zero or
    more, one or more, or zero or one, respectively.  (See note, below.)
    Defaults to None (no files expected).

    :param devel: Whether or not to include `-d` (`--dev`, `--devel`). Defaults to
    False. Accessed as `CONFIG.devmode` (True/False).

    :param trace: Whether or not to include a `--trace` option. Defaults to
    False. Accessed as `CONFIG.loglevel` (set to `TRACE`).

    :param configfile: Whether or not to include `-c` (`--configfile`) option.
    Defaults to False. Accessed as `CONFIG.configfile` (set to whatever name
    folows the `-c`).

    :param configfile_default: The name (and path) of the default config file
    (implies configfile=True). Defaults to "".

    :param logfile: Whether or not to include an `-l` (`--logfile`) option.
     Defaults to False. Accessed as `CONFIG.logfile` (set to whatever name
    folows the `-l`).

    :param logfile_default: The name (and path) of the default log file to
    produce (implies logfile=True). Defaults to "".

    :param infile: Whether or not to include an -i (`--infile`) option.
    Defaults to False. Accessed as `CONFIG.infile` (set to whatever name
    folows the `-i`).

    :param outfile: Whether or not to include an -o (`--outfile`) option.
    Defaults to False. Accessed as `CONFIG.outfile` (set to whatever name
    folows the `-o`).

    :param recurse: Whether or not to include a -r (`--recurse`) option.
    Defaults to False. Accessed as `CONFIG.recurse` (True/False).

    :return: The initialized `argparse.ArgumentParser` instance (which can
    be configured further).

    NOTE: If both `command`=True and `filenames`=something, then the command
    will be required. If `command`=True but `filenames` is not specified, then
    the command will be optional (with a default value of `"gui"`).
    """
    parser = ArgumentParser(description="")
    if version_text:
        parser.add_argument("--version", action="version", version=version_text)
    if command:
        if filenames:
            parser.add_argument('command', nargs=1)
        else:
            parser.add_argument('command', nargs="?", default="gui")
    if filenames:
        parser.add_argument("filenames", nargs=filenames, help="one or more files to be processed")
    if devel:
        parser.add_argument("-d", "--dev", "--devel", dest="devmode", help="turns on developer mode", action="store_true", default=False)
    if verbose:
        parser.add_argument("-v", "--verbose", dest="loglevel", help="prints informative messages", action="store_const", const=DIAGNOSTIC, default=INFO)
    if very_verbose:
        parser.add_argument("--vv", "--very-verbose", "--debug", dest="loglevel", help="prints detailed (debugging) messages", action="store_const", const=DEBUG)
    if trace:
        parser.add_argument("--trace", dest="loglevel", help="prints super-verbose (debugging and tracing) messages", action="store_const", const=TRACE)
    if nocolor:
        parser.add_argument("--nocolor", dest="nocolor", help="turns off coloring the log messages that are sent to the console", action="store_true", default=False)
    if logfile or logfile_default:
        parser.add_argument("-l", "--logfile", dest="logfile", help=f"specifies the name (and path) for the log file (({logfile_default if logfile_default else 'None'} by default)", default=logfile_default)
    if configfile or configfile_default:
        parser.add_argument("-c", "--configfile", dest="configfile", help=f"specifies the name (and path) for the configuration file ({configfile_default if configfile_default else 'None'} by default)", default=configfile_default)
    if infile:
        parser.add_argument("-i", "--infile", dest="infile", help="specifies the name (and path) for the input file (rather than stdin)", default="")
    if outfile:
        parser.add_argument("-o", "--outfile", dest="outfile", help="specifies the name (and path) for the output file (rather than stdout)", default="")
    if recurse:
        parser.add_argument("-r", "--recurse", dest="recurse", help="searches in subdirectories as well", action="store_true", default=False)
    return parser


_all__ = ["basic_cli_parser"]
