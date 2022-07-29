"""
Command Line Interface support. Helpers for working with argparse.ArgumentParser.
"""
from argparse import ArgumentParser

from .gw_logging import DEBUG, DIAGNOSTIC, INFO, TRACE

# TODO Allow the user to override these (via CONFIG?)
DEFAULTS = {
    "help_text_filenames": "one or more files to be processed",
    "help_text_verbose": "prints informative messages (INFO)",
    "help_text_debug": "prints detailed (INFO and DEBUG) messages",
    "help_text_trace": "prints super-verbose (INFO, DEBUG and TRACE) messages",
    "help_text_devel": "turns on developer mode",
    "help_text_nocolor": "turns off coloring the log messages that are sent to the console",
    "help_text_configfile": "specifies the name (and path) for the configuration file ({} by default)",
    "help_text_logfile": "specifies the name (and path) for the log file ({} by default)",
    "help_text_infile": "specifies the name (and path) for the input file (rather than stdin)",
    "help_text_outfile": "specifies the name (and path) for the output file (rather than stdout)",
    "help_text_recurse": "searches in subdirectories as well",
}


def basic_cli_parser(version_text="", use_subcommands=False,
                     use_verbose_switch=True, use_very_verbose_switch=True, use_trace_switch=False,
                     use_devel_switch=False, use_no_color_switch=True,
                     number_of_file_names_allowed=None,
                     use_config_file_switch=False, config_file_default="",
                     use_log_file_switch=False, log_file_default="",
                     use_in_file_switch=False, use_out_file_switch=False, use_recurse_switch=False
                     ) -> ArgumentParser:
    """
    Instantiates an `argparse.ArgumentParser` with a selection of commonly
    used switches.

    :param version_text: What to display if the `--version` switch is given.
    Defaults to there not being a `--version` switch.

    :param use_subcommands: Use `True` if you allow/require a subcommand to
    appear on the line i.e. an argument without a leading dash. (It's a
    subcommand, since the program itself is the main command.) If so, the
    subcommand may appear before or after any switches. Accessed as
    `CONFIG.command`. (See note, below.)

    :param use_verbose_switch: Whether or not to include a `-v` (`--verbose`)
    option. Defaults to True. Accessed as `CONFIG.log_level` (set to `INFO`).

    :param use_very_verbose_switch: Whether or not to include a `--vv`
    (`--very-verbose`, `--debug`) option. Defaults to True. Accessed as
    `CONFIG.log_level` (set to `DEBUG`).

    :param use_trace_switch: Whether or not to include a `--trace` option.
    Defaults to False. Accessed as `CONFIG.log_level` (set to `TRACE`).

    :param use_devel_switch: Whether or not to include `-d` (`--dev`, `--devel`).
    Defaults to False. Accessed as `CONFIG.dev_mode` (True/False). Use this
    for things like disabling e-mails from actually being sent, and turning on
    a developer's submenu.

    :param use_no_color_switch: Whether or not to include a `--nocolor` option.
    Defaults to True. Accessed as `CONFIG.no_color` (True/False). This is intended
    to be passed on to `config_logger()` to control the console output, but
    you can use it for other things (as well) such as turning on a high-contrast
    theme.

    :param number_of_file_names_allowed: Whether or not you expect any filenames
    to be listed on the command line, and if so, how many (`filenames=3`,
    `filenames="*"`, `filenames="+"`, `filenames="?"`) `--` meaning: a specific
    number, zero or more, one or more, or zero or one, respectively.  (See note,
    below.) Defaults to `None` (no files expected).

    :param use_config_file_switch: Whether or not to include `-c` (`--configfile`)
    option. Defaults to False. Accessed as `CONFIG.config_file` (set to whatever
    name folows the `-c`).

    :param config_file_default: The name (and path) of the default config file
    (implies configfile=True). Defaults to "".

    :param use_log_file_switch: Whether or not to include an `-l` (`--logfile`)
    option. Defaults to False. Accessed as `CONFIG.log_file` (set to whatever
    name folows the `-l`).

    :param log_file_default: The name (and path) of the default log file to
    produce (implies logfile=True). Defaults to "".

    :param use_infile_switch: Whether or not to include an `-i` (`--infile`)
    option. Defaults to False. Accessed as `CONFIG.in_file` (set to whatever
    name folows the `-i`).

    :param use_outfile_switch: Whether or not to include an `-o` (`--outfile`)
    option. Defaults to False. Accessed as `CONFIG.out_file` (set to whatever
    name folows the `-o`).

    :param use_recurse_switch: Whether or not to include a `-r` (`--recurse`)
    option. Defaults to False. Accessed as `CONFIG.recurse` (True/False).

    :return: The initialized `argparse.ArgumentParser` instance (which can
    be configured further).

    NOTE: If both `use_subcommands` is True and `number_of_file_names_allowed`
    is (something), then the subcommand will be required. Conversely, If
    `use_subcommands` is True but `number_of_file_names_allowed` is None, then
    the subcommand will be optional (with a default value of `""`).
    """
    parser = ArgumentParser(description="")
    if version_text:
        parser.add_argument("--version", action="version", version=version_text)
    if use_subcommands:
        if number_of_file_names_allowed:
            parser.add_argument('command', nargs=1)
        else:
            parser.add_argument('command', nargs="?", default="")
    if number_of_file_names_allowed:
        parser.add_argument("filenames", nargs=number_of_file_names_allowed, help=DEFAULTS["help_text_filenames"])
    if use_devel_switch:
        parser.add_argument("-d", "--dev", "--devel",
                            dest="dev_mode",
                            help=DEFAULTS["help_text_devel"],
                            action="store_true",
                            default=False)
    if use_verbose_switch:
        parser.add_argument("-v", "--verbose",
                            dest="log_level",
                            help=DEFAULTS["help_text_verbose"],
                            action="store_const",
                            const=DIAGNOSTIC,
                            default=INFO)
    if use_very_verbose_switch:
        parser.add_argument("--vv", "--very-verbose", "--veryverbose", "--debug",
                            dest="log_level",
                            help=DEFAULTS["help_text_debug"],
                            action="store_const",
                            const=DEBUG)
    if use_trace_switch:
        parser.add_argument("--trace",
                            dest="log_level",
                            help=DEFAULTS["help_text_trace"],
                            action="store_const",
                            const=TRACE)
    if use_no_color_switch:
        parser.add_argument("--nocolor", "--no-color",
                            dest="no_color",
                            help=DEFAULTS["help_text_nocolor"],
                            action="store_true",
                            default=False)
    if use_log_file_switch or log_file_default:
        parser.add_argument("-l", "--logfile", "--log-file",
                            dest="log_file",
                            help=DEFAULTS["help_text_logfile"].format(log_file_default if log_file_default else 'None'),
                            default=log_file_default)
    if use_config_file_switch or config_file_default:
        parser.add_argument("-c", "--configfile", "--config-file",
                            dest="config_file",
                            help=DEFAULTS["help_text_configfile"].format(config_file_default if config_file_default else 'None'),
                            default=config_file_default)
    if use_in_file_switch:
        parser.add_argument("-i", "--infile", "--in-file",
                            dest="in_file",
                            help=DEFAULTS["help_text_infile"],
                            default="")
    if use_out_file_switch:
        parser.add_argument("-o", "--outfile", "--out-file",
                            dest="out_file",
                            help=DEFAULTS["help_text_outfile"],
                            default="")
    if use_recurse_switch:
        parser.add_argument("-r", "--recurse",
                            dest="recurse",
                            help=DEFAULTS["help_text_recurse"],
                            action="store_true",
                            default=False)
    return parser


_all__ = ["basic_cli_parser"]
