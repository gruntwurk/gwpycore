"""
Example starting point for any app that wants to take advantage of
of the following baseline gwpycore features:

- Command-line parsing
- Config file (INI) parsing
- Enahnced logging

"""
import logging
import re
import sys
from pathlib import Path
from argparse import ArgumentParser
from typing import Optional, Union

from gwpycore import (GWConfigParser, GlobalSettings, basic_cli_parser,
                      NamedColor,
                      setup_logging, TRACE, DIAGNOSTIC,
                      EX_OK, EX_ERROR, EX_WARNING, EX_CONFIG)

# These two lines will be repeated in every .py file in your app (if needed)
# GlobalSettings is a singleton class, meaning that it will be constructed here
# (being the first time that GlobalSettings() is called), but thereafter it just
# returns a reference to the same object instead of constructing a new one.
CONFIG = GlobalSettings()
LOG = logging.getLogger(__name__)

CONFIG_FILE_DEFAULT = "examples/general_example.ini"
DEFAULT_LOG_FILE_NAME = "general_example.log"

__version__ = "0.0.1"  # For demo purposes. You might actually handle your versioning another way.


def load_command_line(args):
    """
    Parses the command-line switches and adds the corresponding values to CONFIG.

    (If your app doesn't need command-line parsing, then just leave this function out.)

    (TODO Create a `gwcli` snippet for this function.)
    """
    YES = True
    NO = False
    # Here we instatiate Python's built-in ArgumentParser, and then load it up
    # with a bunch of commonly-used switches...
    parser: ArgumentParser = basic_cli_parser(
        version_text=__version__,
        command=YES,  # accessed as CONFIG.command
        devel=YES,  # --devel switch: means CONFIG.dev_mode will be True/False
        trace=NO,  # --trace switch: means CONFIG.log_level will be TRACE
        log_file=YES,  # --logfile <filename>: accessed as CONFIG.log_file
        log_file_default=DEFAULT_LOG_FILE_NAME,
        config_file=YES,  # --configfile <filename>: accessed as CONFIG.config_file
        config_file_default=CONFIG_FILE_DEFAULT,
        no_color=YES  # --nocolor switch: means CONFIG.no_color will be True/False
    )
    # And now for an app-specific switch. (Notice that for each of the YES/NO
    # choices above, you would have had to do something like the following
    # yourself.)
    parser.add_argument('-r', '--restricted', '--classified', '--top-secret',
                        dest="is_restricted",
                        help='Specifies that the app is dealing with sensitive info.',
                        action="store_true",
                        default=False)

    switches = parser.parse_args(args)  # noqa F811

    # For this demo, we're forcing the logging level to include DIAGNOSTIC, DEBUG
    # and TRACE (as if the command line specified --very-verbose).
    switches.log_level = min(switches.log_level, TRACE)

    # Here we take advantage of CONFIG being an instance of our GlobalSettings()
    # class (as opposed to any other dict-like object). The update_as_immutable()
    # method tells GlobalSettings not to allow any further changes to these
    # particular settings. We do this here because the command-line switches need
    # to take precedence over anything in the config file, but the command-line
    # switches have to be loaded first.
    CONFIG.update_as_immutable(switches)


def load_config(config_file: Union[Path, str]):
    """
    So far, CONFIG contains the command-line switches. Here, we'll add the
    values of the configuration INI file (if there is one) and/or set various
    default values.

    (If your app doesn't need an INI config file, then just leave this
    function out.)

    (TODO Create a `gwconfig` snippet for this function.)
    """
    if not config_file:
        LOG.info("No config file specified.")
        return

    # This next bit isn't really part of the example, it's just so that you can
    # run this example from within the `examples` folder or its parent folder.
    config_file = Path(config_file)
    if not config_file.exists():
        config_file = config_file.parent.parent / config_file.name
    if not config_file.exists():
        LOG.warning("Config file {} does not exist!".format(str(config_file)))
        return

    LOG.info("Loading config file {}".format(str(config_file)))
    config_parser = GWConfigParser(config_file)

    # Here is another advantage to using our GlobalSettings class for CONFIG.
    # You can import a setting from the config parser into the GlobalSettings
    # in a single, uncomplicated call.
    CONFIG.import_setting('serif typeface', section='display', default='Times New Roman', config_parser=config_parser)
    # In this case, the setting name ('serif typeface') has to be specified
    # with a space since that's how it appears in the INI file, but GlobalSettings
    # will normalize it to use an underscore (so that you can refer to it as an
    # attribute (CONFIG.serif_typeface).

    # Notice that the following calls don;t need to repeat config_parser=config_parser.
    # It remembers.
    CONFIG.import_setting('sans-typeface', section='display', default='Arial')
    # Again, GlobalSettings will normalize the hyphen in 'sans-typeface' to an
    # underscore.

    # Here we invoke one of the converters that the config parser knows about.
    # In this case, it's one that we told it about.
    CONFIG.import_setting('text_background', section='display', how='named_color', default=NamedColor.COBALTGREEN)

    # And even provide our own on-the-spot conversion routine (e.g. ignore any non-digits)
    def as_int_forgiving(x):
        return int(re.sub(r'[^0-9]+', '', x))
    CONFIG.import_setting('cycle days', section='backups', how=as_int_forgiving, default=30)


def further_initialization():
    """
    Example of how you might follow up after parsing the command line and/or
    loading a config file.

    (TODO Create a `gwfurther` snippet for this function.)
    """
    LOG.trace("Performing further initialization")
    CONFIG.application_title = "My Application"
    CONFIG.version = __version__

    if CONFIG.dev_mode:
        LOG.info("Running in dev mode.")
        # TODO Place special setup code for dev mode here (e.g. suppressing
        # actual web service calls, not actually sending any emails)


def do_something_useful() -> int:
    CONFIG.status = 'bad'

    for line in CONFIG.dump():
        LOG.debug(line)

    if CONFIG.status == 'good':
        return EX_OK
    if CONFIG.status == 'bad':
        return EX_WARNING
    if CONFIG.status == 'ugly':
        return EX_ERROR
    return EX_CONFIG


def finish(exit_code=0, exception: Optional[Exception] = None):
    """
    Housekeeping for when the app shuts down.

    (TODO Create a `gwfinish` snippet for this function.)
    """
    LOG.trace("Finishing")
    if exception:
        exit_code = 1
        if hasattr(exception, "exit_code"):
            exit_code = exception.exit_code
        LOG.uncaught(exception)
    LOG.diagnostic(f"Exit code = {exit_code}")


def main():
    """
    (TODO Create a `gwmain` snippet for this function.)
    """
    load_command_line(sys.argv[1:])  # into CONFIG

    # Here, we have gwpycore enhance the logging and reconfigure the root
    # logger (according to the command-line switches we just processed)
    setup_logging({
        "log_level": CONFIG.log_level if CONFIG.log_level else DIAGNOSTIC,
        "log_file": CONFIG.log_file,
        "log_file_level": TRACE,
        "no_color": CONFIG.no_color})  # with the GruntWork enhancements
    # And now that we have a configured logger, we can do some catching up
    LOG.trace("(Previously) Loaded command line and set up logging.")

    try:
        load_config(config_file=CONFIG.config_file)
        further_initialization()

        # fire off the main application code here
        exit_code = do_something_useful()

        finish(exit_code=exit_code)
    except Exception as e:
        finish(exception=e)


if __name__ == "__main__":
    main()
