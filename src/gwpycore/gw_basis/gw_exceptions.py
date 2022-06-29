from .gw_logging import DEBUG, ERROR, WARNING

# This list of suggested exit codes is based on https://www.freebsd.org/cgi/man.cgi?query=sysexits
EX_OK = 0
EX_WARNING = 1  # Execution completed, but there were warning(s) reported
EX_ERROR = 2  # Execution failed (with an unspecified reason)
EX_USAGE = 64  # The command was used incorrectly (bad arguments, bad flag, etc.)
# EX_DATAERR = 65 # Bad input data
# EX_NOINPUT = 66 # Input file doesn't exist/unreadable.
# EX_NOUSER = 67
# EX_NOHOST = 68
# EX_UNAVAILABLE = 69 # A service is unavailable.
EX_SOFTWARE = 70  # An internal software error has been detected.
# EX_OSERR = 71 # An operating system error has been detected.
# EX_OSFILE = 72 # Some system file does not exist/unreadable/has syntax error.
# EX_CANTCREAT = 73 # A (user specified) output file cannot be created.
# EX_IOERR = 74 # An error occurred while doing I/O on some file.
EX_TEMPFAIL = 75 # Temporary failure, indicating something that is not really an error.
# EX_PROTOCOL = 76 # The remote system returned something that was not possible during a protocol exchange.
# EX_NOPERM = 77 # Insufficient permission.
EX_CONFIG = 78  # Something was found in an unconfigured or miscon­figured state.
# EX_INTERNAL = 123 # FYI: black (the python fomatter) returns this code for an internal error.


class GruntWurkError(Exception):
    """
    Exception raised for a general, insurmountable error.
    Also, serves as a base-class for the more specific errors below.

    Attributes:
        message -- explanation of the error
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.ERROR.
    """

    exitcode: int = EX_ERROR
    loglevel = ERROR

    def __init__(self, message, loglevel=ERROR):
        self.exitcode = EX_ERROR
        self.message = message
        self.loglevel = loglevel

    def __str__(self) -> str:
        return self.message

class GruntWurkWarning(GruntWurkError):
    """
    Exception raised for a general warning.
    Also, serves as a base-class for the more specific warnings below.

    Attributes:
        message -- explanation of the warning(s)
        loglevel (optional) -- How this warning should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.WARNING.
    """

    # TODO Consider changing this to descend from UserWarning
    def __init__(self, message, loglevel=WARNING) -> None:
        super(GruntWurkWarning, self).__init__(message, loglevel)
        self.exitcode = EX_WARNING  # Don't exit, carry on


class GruntWurkValueError(GruntWurkError):
    """
    Exception raised because of a bad value.

    Attributes:
        message -- explanation of the error(s)
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.ERROR.
    """

    def __init__(self, message, loglevel=ERROR):
        super(GruntWurkValueError, self).__init__(message, loglevel)
        self.exitcode = EX_USAGE


class GruntWurkConfigError(GruntWurkError):
    """
    Exception raised because of bad data in a config file or something wrong with our operating environment.

    Attributes:
        message -- explanation of the error(s)
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.ERROR.
    """

    def __init__(self, message, loglevel=ERROR):
        super(GruntWurkConfigError, self).__init__(message, loglevel)
        self.exitcode = EX_CONFIG

class GruntWurkFileError(GruntWurkError):
    """
    Exception raised because of a problem managing files or directories.

    Attributes:
        message -- explanation of the error(s)
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.ERROR.
    """

    def __init__(self, message, loglevel=ERROR):
        super(GruntWurkFileError, self).__init__(message, loglevel)


class GruntWurkConfigSettingWarning(GruntWurkWarning):
    """
    Warning raised because of a bad setting in a config file.

    Attributes:
        key -- the name of the setting
        attempted_value -- the value that is in error
        possible_values -- (optional) a list of valid choices
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.WARNING.
    """

    def __init__(self, key, attempted_value, possible_values=None, loglevel=WARNING):
        msg = f"The configuration setting of {key} = {attempted_value} is invalid."
        if possible_values:
            msg += f" Possible values are: {possible_values}"
        super(GruntWurkConfigSettingWarning, self).__init__(msg, loglevel)


class GruntWurkUserEscape(GruntWurkError):
    """
    Exception raised because the user canceled out of an operation.

    Attributes:
        message (optional) -- explanation of the error(s)
        loglevel (optional) -- How this error should appear in the log (if no
            outer code catches it and handles it, that is). The default is
            logging.DEBUG.
    """

    def __init__(self, message="", loglevel=DEBUG):
        super(GruntWurkUserEscape, self).__init__(message, loglevel)
        self.exitcode = EX_TEMPFAIL


__all__ = [
    "GruntWurkError",
    "GruntWurkWarning",
    "GruntWurkValueError",
    "GruntWurkFileError",
    "GruntWurkConfigError",
    "GruntWurkConfigSettingWarning",
    "GruntWurkUserEscape",
    "EX_OK",
    "EX_WARNING",
    "EX_ERROR",
    "EX_USAGE",
    "EX_SOFTWARE",
    "EX_CONFIG"
    ]
