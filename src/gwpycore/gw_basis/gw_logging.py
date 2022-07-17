import argparse
import logging
import logging.handlers
import sys
from typing import Optional, IO
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

# ############################################################################
#                                                                   FORMATTERS
# ############################################################################

UNTHREADED_FORMAT = logging.Formatter(
    fmt='%(asctime)s %(levelname)-10s <%(name)s> %(message)s  %(filename)s %(lineno)d %(funcName)s',
    datefmt='%Y-%m-%d %H:%M:%S')

THREADED_FORMAT = logging.Formatter(
    fmt = '%(asctime)s %(levelname)-10s <%(name)s> %(process)d %(thread)d %(message)s  %(filename)s %(lineno)d %(funcName)s',
    datefmt='%Y-%m-%d %H:%M:%S')


class GruntWurkConsoleHandler(colorlog.StreamHandler):
    def __init__(self) -> None:
        super().__init__()
        self.set_name("colored_console")
        self.setStream(sys.stderr)
        self.setFormatter(GruntWurkColoredFormatter())


class GruntWurkColoredFormatter(colorlog.ColoredFormatter):
    """
    Our take on the standard colorlog.ColoredFormatter.
    The default color palette includes our new TRACE and DIAGNOSTIC levels.
    The default format string only shows the level name as colored, while the
    message is always white (to make it easy to read).
    """
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: str = "%", log_colors=None, reset: bool = True,
                 secondary_log_colors=None, validate: bool = True, stream: Optional[IO] = None, no_color: bool = False, force_color: bool = False) -> None:
        fmt = "[%(log_color)s%(levelname)-7s%(reset)s] %(white)s%(message)s"
        datefmt = '%H:%M:%S'

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
                         #  validate=validate,
                         #  stream=stream,
                         #  no_color=no_color,
                         #  force_color=force_color
                         )


# ############################################################################
#                                                                        SETUP
# ############################################################################

def setup_logging() -> None:
    """
    Enhances the standard Python logging (as follows). Thereafter, calling
    the standard logging.getlogger(name) will return a logger instance that
    includes:

    - An additional logging level called DIAGNOSTIC (between INFO and DEBUG)
    - A corresponding log.diagnostic() method
    - An additional logging level called TRACE (even more chatty than DEBUG)
    - A corresponding log.trace() method
        Note: there are ways to automatically trace program execution without
        having to manually add log.trace() calls. This is intended to be for
        targeted areas of concern.
    - An enhanced log.exception() method -- in this version if there is an
        e.loglevel attribute, it will be used instead of assuming ERROR.
    - A new log.uncaught() method -- same as log.exception(), but first calls
        log.error("The following ... should have been caught ...")
    - Colorized console output (optional).

    :return: None
    """

    def diagnostic(self, message, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Halfway between INFO and DEBUG, this is a technical log entry (i.e. intended for the developer, not the user).
        Think of it as a special DEBUG entry that should be highlighted.
        """
        if self.isEnabledFor(DIAGNOSTIC):
            self._log(DIAGNOSTIC, message, args, **kws)

    logging.addLevelName(DIAGNOSTIC, "DIAGNOSTIC")
    logging.Logger.diagnostic = diagnostic

    def trace(self, message, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Even more verbose than DEBUG, trace logs might be scattered throughout the code, especially at entry and exit points.
        ("Killroy was here.")
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kws)

    logging.addLevelName(TRACE, "TRACE")
    logging.Logger.trace = trace

    def per_exception(self, e: Exception, *args, exc_info=True, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        This overrides the default logger method of `exception` with one that
        checks the exception itself for an indication of what logging level
        to use, instead of just assuming ERROR. Specifically, if the exception
        has a `loglevel` attribute, that's what will be used.

        See also: `GruntWurkException`.
        """
        level = ERROR
        if hasattr(e, "loglevel"):
            level = e.loglevel
        if self.isEnabledFor(level):
            self._log(level, e, args, exc_info=exc_info, **kws)

    logging.Logger.exception = per_exception

    def uncaught(self, e: Exception, *args, **kws):  # pragma no cover
        # Note: logger takes its '*args' as 'args'.
        """
        Same as exception(), except it first logs a note (at error level) that
        the error should have been caught earlier.
        Note: This is not usually called directly. It's usually just called
        from within the provided `log_uncaught` function, which is placed in
        the outermost try/cath of your application.
        """
        self.error("Uncaught error detected. There is no good reason why the following error wasn't handled earlier.")
        self.exception(e)

    logging.Logger.uncaught = uncaught

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

    :param log: The Logger to use. If not specified, then the logger with the
    name "main" will be used.

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
        log = logging.getLogger("main")
    log.trace("Enter: log_uncaught()")
    exitcode = EX_OK
    if exception:
        exitcode = EX_ERROR
        if hasattr(exception, "exitcode"):
            exitcode = exception.exitcode
        log.uncaught(exception)
    return exitcode

# ############################################################################
#                                                                  MAKE LOGGER
# ############################################################################


def make_logger(name: str, level: int = INFO, log_file: str = None, file_level: int = DEBUG, config: Optional[argparse.Namespace] = None) -> logging.Logger:
    """
    Makes (or modifies) a logger by the given name. This is indended to be
    called once per root name. For example, if you call `make_logger("foo", ...)`
    and subsequently call `LOG = logging.getLogger("foo.bar")`, the foo.bar logger
    will inherit the configuration of foo.

    :param name: Name of the logger (typically __name__, but could be something
    explicit like "gui" or "print".)

    :param level: Minimum logging level to show in the console, defaults to INFO.

    :param log_file: Optional root filename for a logging file (using a
    RotatingFileHandler), defaults to None.

    :param file_level: Minimum logging level to show in the log file, defaults
    to DEBUG.

    :param config: An optional configuration (an argparse.Namespace instance)
    that contributes various settings, defaults to None.

    :return: The constructed logger, for convenience. (Thereafter, use
    `LOG = logging.getLogger("<name>")` to obtain a reference.
    """
    log = logging.getLogger(name)
    log.setLevel(min(level, file_level))
    if len(log.handlers) == 0:
        console_handler = GruntWurkConsoleHandler()
        console_handler.setLevel(level)
        log.addHandler(console_handler)

        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)
            file_handler.setFormatter(UNTHREADED_FORMAT)
            file_handler.setLevel(file_level)
            log.addHandler(file_handler)
    return log


__all__ = [
    "setup_logging",
    "GruntWurkConsoleHandler",
    "GruntWurkColoredFormatter",
    "log_uncaught",
    "make_logger",
    "CRITICAL", "ERROR", "WARNING", "INFO", "DIAGNOSTIC", "DEBUG", "TRACE",
]
