import logging
import logging.handlers
import sys
from typing import Dict, Optional
import colorlog

CRITICAL = logging.CRITICAL  # aka. FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING  # aka. WARN
INFO = logging.INFO
DIAGNOSTIC = INFO - 5
DEBUG = logging.DEBUG
TRACE = DEBUG - 5

# Note: we are re-defining these here rather than importing them from
# gw_exceptions to avoid a circular reference.
EX_OK = 0
EX_WARNING = 1
EX_ERROR = 2

MAX_LOGFILE_SIZE_BYTES = 1000000  # TODO make this a CONFIG setting
MAX_LOGFILE_ROTATIONS = 3  # TODO make this a CONFIG setting


# ############################################################################
#                                                                   FORMATTERS
# ############################################################################

COLORED_FORMAT_CONSOLE = "[%(log_color)s%(levelname)-7s%(reset)s] %(white)s%(message)s"
UNCOLORED_FORMAT_CONSOLE = "[%(levelname)-7s] %(message)s"
DATE_FORMAT_CONSOLE = '%H:%M:%S'
DATE_FORMAT_LOGFILE = '%Y-%m-%d %H:%M:%S'

UNTHREADED_FORMAT_LOGFILE = logging.Formatter(
    fmt='%(asctime)s %(levelname)-10s <%(name)s> %(message)s  %(filename)s %(lineno)d %(funcName)s',
    datefmt=DATE_FORMAT_LOGFILE)

# TODO make using this variant a CONFIG setting and/or allow CONFIG to specify a whole different pair of formats.
THREADED_FORMAT_LOGFILE = logging.Formatter(
    fmt='%(asctime)s %(levelname)-10s <%(name)s> %(process)d %(thread)d %(message)s  %(filename)s %(lineno)d %(funcName)s',
    datefmt=DATE_FORMAT_LOGFILE)


class GruntWurkConsoleHandler(colorlog.StreamHandler):
    """
    Our take on a console handler, which uses our GruntWurkColoredFormatter.
    """
    def __init__(self, no_color=False) -> None:
        super().__init__()
        self.set_name("colored_console")
        self.setStream(sys.stderr)
        self.setFormatter(GruntWurkColoredFormatter(no_color=no_color))


class GruntWurkColoredFormatter(colorlog.ColoredFormatter):
    """
    Our take on the standard colorlog.ColoredFormatter.
    The default color palette includes our new TRACE and DIAGNOSTIC levels.
    The default format string only shows the level name as colored, while the
    message is always white (to make it easy to read).
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None,
                 style: str = "%", log_colors=None, reset: bool = True,
                 secondary_log_colors=None, no_color: bool = False) -> None:
        if not fmt:
            # fmt = UNCOLORED_FORMAT_CONSOLE if no_color else COLORED_FORMAT_CONSOLE
            fmt = COLORED_FORMAT_CONSOLE
        if not datefmt:
            datefmt = DATE_FORMAT_CONSOLE

        # Color choices are: black, red, green, yellow, blue, purple, cyan, white
        # Prefix choices are: bold_, thin_, bg_, bg_bold_
        log_colors = {
            "TRACE": "blue",
            "DEBUG": "cyan",
            "DIAGNOSTIC": "purple",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white"
        }
        super().__init__(fmt=fmt,
                         datefmt=datefmt,
                         style=style,
                         log_colors=log_colors,
                         reset=reset,
                         secondary_log_colors=secondary_log_colors,
                         no_color=no_color,
                         )


# ############################################################################
#                                                                        SETUP
# ############################################################################

def setup_logging(config: Dict = None) -> None:
    """
    Enhances the standard Python logging mechanism (as follows). Thereafter,
    calling the standard `logging.getlogger(name)` will return a logger
    instance that includes:

    - An additional logging level called `DIAGNOSTIC` (between `INFO` and `DEBUG`)
    - A corresponding `log.diagnostic()` method
    - An additional logging level called `TRACE` (even more chatty than `DEBUG`)
    - A corresponding `log.trace()` method
        Note: there are ways to automatically trace program execution without
        having to manually add log.trace() calls. This is intended to be for
        targeted areas of concern.
    - An enhanced `log.exception()` method -- in this version, if there is an
        `e.loglevel` attribute, it will be used instead of assuming `ERROR`.
    - A new `log.uncaught()` method -- same as `log.exception()`, but first calls
        `log.error("The following ... should have been caught ...")`
    - Colorized console output.

    :param config: An optional dictionary-like object that specifies how to
    configure the root logger. If a dict is specified, then `config_logger()`
    is called against the root logger (which overwrites any existing handlers
    with our own).

    :return: None
    """

    # FIXME override the main logging method with one that handles UnicodeEncodeError.

    def diagnostic(self, message, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Halfway between INFO and DEBUG, this is a technical log entry
        (i.e. intended for the developer, not the user).
        Think of it as a special DEBUG entry that should be highlighted.
        """
        if self.isEnabledFor(DIAGNOSTIC):
            self._log(DIAGNOSTIC, message, args, **kws)

    logging.addLevelName(DIAGNOSTIC, "DIAGNOSTIC")
    logging.Logger.diagnostic = diagnostic

    def trace(self, message, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Even more verbose than DEBUG, trace logs might be scattered throughout
        the code, especially at entry and exit points. ("Killroy was here.")
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kws)

    logging.addLevelName(TRACE, "TRACE")
    logging.Logger.trace = trace

    def per_exception(self, e: Exception, *args, exc_info=True, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        This overrides the default logger method of `.exception()` with one that
        checks the exception itself for an indication of what logging level
        to use, instead of just assuming `ERROR`. Specifically, if the exception
        has a `loglevel` attribute (or `log_level`), that's what will be used.

        See also: `GruntWurkException`.
        """
        level = ERROR
        if hasattr(e, "loglevel"):
            level = e.loglevel
        if hasattr(e, "log_level"):
            level = e.log_level
        if self.isEnabledFor(level):
            self._log(level, e, args, exc_info=exc_info, **kws)

    logging.Logger.exception = per_exception

    def uncaught(self, e: Exception, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Same as `.exception()`, except it first logs a note (at error level) that
        the error should have been caught earlier.
        NOTE: This is not usually called directly. It's usually just called
        from within the provided `log_uncaught()` function, which is placed in
        the outermost `try/catch` of your application.
        """
        self.error("Uncaught error detected. There is no good reason why the following error wasn't handled earlier.")
        self.exception(e)

    logging.Logger.uncaught = uncaught

    if config:
        config_logger(None, config)


# ############################################################################
#                                                                     UNCAUGHT
# ############################################################################


def log_uncaught(exception: Optional[Exception] = None, log: logging.Logger = None) -> int:
    """
    It's always a good idea to wrap the entire application in a `try/except`
    block in order to catch any exceptions that trickle all the way up to
    that point. Then, just call this function in the `except` clause, passing in
    the offending Exception.

    TIP: For a `Kivy` app, just call `gwpykivy.manage_uncaught_exceptions_within_kivy()`
    from within the `__init__` method of your app's main class (the class that
    inherits from `APP` or `MDApp`). That will register a special exception
    handler that does the work of sorting out any uncaught exceptions -- exactly
    how this function does -- including  telling kivy to carry on running if
    the exception specifies an exit code of `EX_OK` (0) or `EX_WARNING` (1).

    :param exception: The otherwise uncaught exception.

    :param log: The Logger to use. If not specified, then the root logger
    will be used.

    :return: A suggested exit code. If the exception has an `exitcode`
    attribute (see `GruntWurkException`), then that code is returned;
    otherwise, `EX_ERROR` (2) is returned -- or in the case that `exception`
    is None (somehow), then `EX_OK` (0) is returned.

    IMPORTANT: It's possible that an exception has an associated exit code of
    `EX_WARNING` (1), or even `EX_OK` (0). Thus, if the returned code is <= 1,
    then the application should probably actually continue, relying on the
    fact that exception has (just now) been logged.
    """
    if not log:
        log = logging.getLogger()
    log.trace("Enter: log_uncaught()")
    exitcode = EX_OK
    if exception:
        exitcode = EX_ERROR
        if hasattr(exception, "exitcode"):
            exitcode = exception.exitcode
        log.uncaught(exception)
    return exitcode

# ############################################################################
#                                                                CONFIG LOGGER
# ############################################################################


def config_logger(name: str, config: Dict) -> logging.Logger:
    """
    Makes (or modifies) a logger by the given name to establish our
    `GruntWurkConsoleHandler` as the main handler, and then optionally adds a
    `RotatingFileHandler`. IMPORTANT: Any existing handlers will be deleted first.

    TIP: If you pass a configuration dictionary into `setup_logging()` then
    this function will be called automatically to configure the root logger.
    Thus, this function would normally only be called directly in the event
    that a non-root logger needs to be configured differently than the root.

    :param name: Name of the logger to configure (or `None` for the root logger).
    Configuring the root logger (None) is usual, but configuring special loggers
    for special purposes is also reasonable. For example, this `gwpycore` library
    itself configures a "gwpy" logger that (occasionally) sends messages to a
    `gwpy.log` file (as well as the console).

    :param config: A configuration object (e.g. an `argparse.Namespace`
    instance, or a simple dictionary) that contributes the settings to be
    applied to the logger. The possible settings are:

    `config["log_level"]` -- The minimum logging level to show in the console,
    defaults to `INFO`.

    `config["log_file"]` -- Optional (root) filename for a logging file (using a
    `RotatingFileHandler`), defaults to `None`.

    `config["log_file_level"]` -- The minimum logging level to show in the log
    file, if there is one, defaults to `DEBUG`.

    `config["log_file_size"]` -- The maximum size for a log file (default is 1MB)

    `config["log_file_rotations"]` -- The maximum number of log file rotations,
    as in `my.log` -> `my.log.1` -> `my.log.2` -> ... (the default is 3).

    `config["no_color"]` -- Whether or not to turn off colorizing the console
    output. The default is False. (Tip: Changing it to true is useful in unit
    tests that capture `stdout`/`stderr`.)

    :return: The constructed logger, for convenience. (Thereafter, use
    `LOG = logging.getLogger("<name>")` to obtain a reference.
    """
    if not isinstance(config, Dict):
        # Note: We cannot raise a GruntWurkConfigError here, because it would be a circular reference
        raise Exception(
            "config_logger requires a config object that is Dict-like (e.g. GlobalSettings, argparse.Namespace, or a plain dictionary.")

    console_level = config["log_level"] if "log_level" in config else INFO
    log_file = config["log_file"] if "log_file" in config else None
    file_level = config["log_file_level"] if "log_file_level" in config else DEBUG
    max_bytes = config["log_file_size"] if "log_file_size" in config else MAX_LOGFILE_SIZE_BYTES
    backup_count = int(config["log_file_rotations"]) if "log_file_rotations" in config else MAX_LOGFILE_ROTATIONS
    no_color = config["no_color"] if "no_color" in config else False

    log = logging.getLogger(name)
    log.setLevel(min(console_level, file_level if log_file else console_level))
    log.handlers.clear()
    console_handler = GruntWurkConsoleHandler(no_color=no_color)
    console_handler.setLevel(console_level)
    log.addHandler(console_handler)

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(UNTHREADED_FORMAT_LOGFILE)
        file_handler.setLevel(file_level)
        log.addHandler(file_handler)
    return log


__all__ = [
    "setup_logging",
    "config_logger",
    "GruntWurkConsoleHandler",
    "GruntWurkColoredFormatter",
    "log_uncaught",
    "CRITICAL", "ERROR", "WARNING", "INFO", "DIAGNOSTIC", "DEBUG", "TRACE",
]
