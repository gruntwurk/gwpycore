"""
Command Line Interface support. Helpers for working with argparse.ArgumentParser.
"""
from argparse import ArgumentParser

from .gw_logging import DEBUG, DIAGNOSTIC, INFO, TRACE


DEFAULTS = {
    "help_text_nocolor": "turns off coloring the log messages that are sent to the console",
    "help_text_trace": "prints super-verbose (debugging and tracing) messages",
    "help_text_debug": "prints detailed (debugging) messages",
    "help_text_configfile": "specifies the name (and path) for the configuration file ({} by default)",
    "help_text_devel": "turns on developer mode",
    "help_text_infile": "specifies the name (and path) for the input file (rather than stdin)",
    "help_text_logfile": "specifies the name (and path) for the log file ({} by default)",
    "help_text_outfile": "specifies the name (and path) for the output file (rather than stdout)",
    "help_text_recurse": "searches in subdirectories as well",
    "help_text_verbose": "prints informative messages",
    "help_text_filenames": "one or more files to be processed"
}


def basic_cli_parser(version_text="", command=False, verbose=True, very_verbose=True,
                     no_color=True, file_names=None, devel=False, trace=False, config_file=False,
                     config_file_default="", log_file=False, log_file_default="", in_file=False,
                     out_file=False, recurse=False) -> ArgumentParser:
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
    Defaults to True. Accessed as `CONFIG.log_level` (set to `INFO`).

    :param very_verbose: Whether or not to include a `--vv` (`--very-verbose`,
    `--debug`) option. Defaults to True. Accessed as `CONFIG.log_level` (set
    to `DEBUG`).

    :param no_color: Whether or not to include a `--nocolor` option. Defaults to
    True. Accessed as `CONFIG.no_color` (True/False).

    :param file_names: Whether or not you expect any filenames to be listed on
    the command line, and if so, how many (`filenames=3`, `filenames="*"`,
    `filenames="+"`, `filenames="?"`) `--` meaning: a specific number, zero or
    more, one or more, or zero or one, respectively.  (See note, below.)
    Defaults to None (no files expected).

    :param devel: Whether or not to include `-d` (`--dev`, `--devel`). Defaults to
    False. Accessed as `CONFIG.dev_mode` (True/False).

    :param trace: Whether or not to include a `--trace` option. Defaults to
    False. Accessed as `CONFIG.log_level` (set to `TRACE`).

    :param config_file: Whether or not to include `-c` (`--configfile`) option.
    Defaults to False. Accessed as `CONFIG.config_file` (set to whatever name
    folows the `-c`).

    :param config_file_default: The name (and path) of the default config file
    (implies configfile=True). Defaults to "".

    :param log_file: Whether or not to include an `-l` (`--logfile`) option.
     Defaults to False. Accessed as `CONFIG.log_file` (set to whatever name
    folows the `-l`).

    :param log_file_default: The name (and path) of the default log file to
    produce (implies logfile=True). Defaults to "".

    :param infile: Whether or not to include an -i (`--infile`) option.
    Defaults to False. Accessed as `CONFIG.in_file` (set to whatever name
    folows the `-i`).

    :param outfile: Whether or not to include an -o (`--outfile`) option.
    Defaults to False. Accessed as `CONFIG.out_file` (set to whatever name
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
        if file_names:
            parser.add_argument('command', nargs=1)
        else:
            parser.add_argument('command', nargs="?", default="gui")
    if file_names:
        parser.add_argument("filenames", nargs=file_names, help=DEFAULTS["help_text_filenames"])
    if devel:
        parser.add_argument("-d", "--dev", "--devel",
                            dest="dev_mode",
                            help=DEFAULTS["help_text_devel"],
                            action="store_true",
                            default=False)
    if verbose:
        parser.add_argument("-v", "--verbose",
                            dest="log_level",
                            help=DEFAULTS["help_text_verbose"],
                            action="store_const",
                            const=DIAGNOSTIC,
                            default=INFO)
    if very_verbose:
        parser.add_argument("--vv", "--very-verbose", "--veryverbose", "--debug",
                            dest="log_level",
                            help=DEFAULTS["help_text_debug"],
                            action="store_const",
                            const=DEBUG)
    if trace:
        parser.add_argument("--trace",
                            dest="log_level",
                            help=DEFAULTS["help_text_trace"],
                            action="store_const",
                            const=TRACE)
    if no_color:
        parser.add_argument("--nocolor", "--no-color",
                            dest="no_color",
                            help=DEFAULTS["help_text_nocolor"],
                            action="store_true",
                            default=False)
    if log_file or log_file_default:
        parser.add_argument("-l", "--logfile", "--log-file",
                            dest="log_file",
                            help=DEFAULTS["help_text_logfile"].format(log_file_default if log_file_default else 'None'),
                            default=log_file_default)
    if config_file or config_file_default:
        parser.add_argument("-c", "--configfile", "--config-file",
                            dest="config_file",
                            help=DEFAULTS["help_text_configfile"].format(config_file_default if config_file_default else 'None'),
                            default=config_file_default)
    if in_file:
        parser.add_argument("-i", "--infile", "--in-file",
                            dest="in_file",
                            help=DEFAULTS["help_text_infile"],
                            default="")
    if out_file:
        parser.add_argument("-o", "--outfile", "--out-file",
                            dest="out_file",
                            help=DEFAULTS["help_text_outfile"],
                            default="")
    if recurse:
        parser.add_argument("-r", "--recurse",
                            dest="recurse",
                            help=DEFAULTS["help_text_recurse"],
                            action="store_true",
                            default=False)
    return parser


_all__ = ["basic_cli_parser"]
