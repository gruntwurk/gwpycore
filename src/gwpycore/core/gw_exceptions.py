from typing import Union
from .gw_logging import DEBUG, ERROR, WARNING

# This list of suggested exit codes is based on https://www.freebsd.org/cgi/man.cgi?query=sysexits
EX_OK = 0
EX_WARNING = 1  # Execution completed, but there were warning(s) reported
EX_ERROR = 2  # Execution failed (with an unspecified reason)
EX_USAGE = 64  # The command was used incorrectly (bad arguments, bad flag, etc.)
# EX_DATAERR = 65  # Bad input data
# EX_NOINPUT = 66  # Input file doesn't exist/unreadable.
# EX_NOUSER = 67
# EX_NOHOST = 68
# EX_UNAVAILABLE = 69 # A service is unavailable.
EX_SOFTWARE = 70  # An internal software error has been detected.
# EX_OSERR = 71  # An operating system error has been detected.
# EX_OSFILE = 72  # Some system file does not exist/unreadable/has syntax error.
# EX_CANTCREAT = 73  # A (user specified) output file cannot be created.
# EX_IOERR = 74  # An error occurred while doing I/O on some file.
EX_TEMPFAIL = 75  # Temporary failure, indicating something that is not really an error.
# EX_PROTOCOL = 76  # The remote system returned something that was not possible during a protocol exchange.
# EX_NOPERM = 77  # Insufficient permission.
EX_CONFIG = 78  # Something was found in an unconfigured or miscon­figured state.
# EX_INTERNAL = 123 # FYI: black (the python fomatter) returns this code for an internal error.


class GWError(Exception):
    """
    Exception raised for a general, insurmountable error. Also, serves as a base
    class for the more specific errors and warnings below.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR.`
    """

    def __init__(self, *args, loglevel=ERROR):
        super().__init__(*args)
        self.exitcode = EX_ERROR
        self.loglevel = loglevel



class GWWarning(GWError):
    """
    Exception raised for a general warning. Also, serves as a base
    class for the more specific warnings below.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.WARNING`.
    """

    # TODO Consider changing this to descend from UserWarning
    def __init__(self, *args, loglevel=WARNING) -> None:
        super().__init__(*args, loglevel)
        self.exitcode = EX_WARNING  # Don't exit, carry on


class GWValueError(GWError):
    """
    Exception raised because of a bad value.
    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel)
        self.exitcode = EX_USAGE


class GWConfigError(GWError):
    """
    Exception raised because of bad data in a config file or something wrong with
    our operating environment.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel)
        self.exitcode = EX_CONFIG


class GWFileError(GWError):
    """
    Exception raised because of a problem managing files or directories.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel)


class GWConfigSettingWarning(GWWarning):
    """
    Warning raised because of a bad setting in a config file.

    :param key: The name of the setting.

    :param attempted_value: The value that is in error.

    :param args: Any additional payload for the exception, e.g. another
    instance of `Exception`).

    :param possible_values: (optional) a list of valid choices.

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.WARNING`.
    """

    def __init__(self, key, attempted_value, *args, possible_values=None, loglevel=WARNING):
        msg = f"The configuration setting of {key} = {attempted_value} is invalid."
        if possible_values:
            msg += f" Possible values are: {possible_values}"
        super(GWConfigSettingWarning, self).__init__(msg, *args, loglevel)


class GWUserEscape(GWError):
    """
    Exception raised because the user canceled out of an operation.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.DEBUG`.
    """

    def __init__(self, *args, loglevel=DEBUG) -> None:
        super().__init__(*args, loglevel)
        self.exitcode = EX_TEMPFAIL


__all__ = [
    "GWError",
    "GWWarning",
    "GWValueError",
    "GWFileError",
    "GWConfigError",
    "GWConfigSettingWarning",
    "GWUserEscape",
    "EX_OK",
    "EX_WARNING",
    "EX_ERROR",
    "EX_USAGE",
    "EX_SOFTWARE",
    "EX_CONFIG"
]
