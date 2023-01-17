from .logging import ERROR, WARNING


__all__ = [
    "GWError",
    "GWWarning",
    "GWValueError",
    "GWIndexError",
    "GWFileNotFoundError",
    "GWFileExistsError",
    "GWNotADirectoryError",
    "GWConfigError",
    "GWConfigSettingWarning",
    "EX_OK",
    "EX_WARNING",
    "EX_ERROR",
    "EX_USAGE",
    "EX_SOFTWARE",
    "EX_CONFIG"
]


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

# Python 3.11 built-in exceptions
# BaseException
#  ├── BaseExceptionGroup
#  ├── GeneratorExit
#  ├── KeyboardInterrupt
#  ├── SystemExit
#  └── Exception
#       ├── ArithmeticError
#       │    ├── FloatingPointError
#       │    ├── OverflowError
#       │    └── ZeroDivisionError
#       ├── AssertionError
#       ├── AttributeError
#       ├── BufferError
#       ├── EOFError
#       ├── ExceptionGroup [BaseExceptionGroup]
#       ├── ImportError
#       │    └── ModuleNotFoundError
#       ├── LookupError
#       │    ├── IndexError
#       │    └── KeyError
#       ├── MemoryError
#       ├── NameError
#       │    └── UnboundLocalError
#       ├── OSError
#       │    ├── BlockingIOError
#       │    ├── ChildProcessError
#       │    ├── ConnectionError
#       │    │    ├── BrokenPipeError
#       │    │    ├── ConnectionAbortedError
#       │    │    ├── ConnectionRefusedError
#       │    │    └── ConnectionResetError
#       │    ├── FileExistsError
#       │    ├── FileNotFoundError
#       │    ├── InterruptedError
#       │    ├── IsADirectoryError
#       │    ├── NotADirectoryError
#       │    ├── PermissionError
#       │    ├── ProcessLookupError
#       │    └── TimeoutError
#       ├── ReferenceError
#       ├── RuntimeError
#       │    ├── NotImplementedError
#       │    └── RecursionError
#       ├── StopAsyncIteration
#       ├── StopIteration
#       ├── SyntaxError
#       │    └── IndentationError
#       │         └── TabError
#       ├── SystemError
#       ├── TypeError
#       ├── ValueError
#       │    └── UnicodeError
#       │         ├── UnicodeDecodeError
#       │         ├── UnicodeEncodeError
#       │         └── UnicodeTranslateError
#       └── Warning
#            ├── BytesWarning
#            ├── DeprecationWarning
#            ├── EncodingWarning
#            ├── FutureWarning
#            ├── ImportWarning
#            ├── PendingDeprecationWarning
#            ├── ResourceWarning
#            ├── RuntimeWarning
#            ├── SyntaxWarning
#            ├── UnicodeWarning
#            └── UserWarning


# ############################################################################
#                                                    (generic) Exception-based
# ############################################################################

class GWException(Exception):
    """
    A mix-in to enhance any Exception to have an associated exit code and an
    associated logging level.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.exitcode = EX_ERROR
        self.loglevel = ERROR


class GWError(GWException):
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


class GWConfigError(GWError):
    """
    Exception raised because of a problem processing configuration data.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel=loglevel)
        self.exitcode = EX_CONFIG


# ############################################################################
#                                                      (generic) Warning-based
# ############################################################################

class GWWarning(Warning, GWException):
    """
    Exception raised for a general warning. Also, serves as a base
    class for the more specific warnings below.

    TIP: In your try/except code, it's suggested to catch `Warning`, in general,
    rather than `GWWarning`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.WARNING`.
    """

    # TODO Consider changing this to descend from UserWarning
    def __init__(self, *args, loglevel=WARNING) -> None:
        super().__init__(*args)
        self.loglevel = loglevel
        self.exitcode = EX_WARNING  # Don't exit, carry on


class GWValueInterpretationWarning(GWWarning):
    """
    Warning raised because of a value that could not be converted to an
    expected type.

    :param key: The name of the field.

    :param attempted_value: The value that is in error.

    :param args: Any additional payload for the exception, e.g. another
    instance of `Exception`).

    :param context: (optional) a description of the context (the data source, row number, etc.).

    :param possible_values: (optional) a list of valid choices.

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.WARNING`.
    """

    def __init__(self, key, attempted_value, *args, context=None, possible_values=None, loglevel=WARNING):
        msg = ""
        if context:
            msg += f"In {context}, "
        msg += f"{key} = {attempted_value} is invalid."
        if possible_values:
            msg += f" Possible values are: {possible_values}"
        super(GWValueInterpretationWarning, self).__init__(msg, *args, loglevel=loglevel)


class GWConfigSettingWarning(GWValueInterpretationWarning):
    """
    Warning raised because of a bad setting in a config file.

    :param key: The name of the setting.

    :param attempted_value: The value that is in error.

    :param args: Any additional payload for the exception, e.g. another
    instance of `Exception`).

    :param context: (optional) a description of the context (the data source, row number, etc.).
    Defaults to "a configuration setting".

    :param possible_values: (optional) a list of valid choices.

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.WARNING`.
    """
    def __init__(self, key, attempted_value, *args, context="a configuration setting", possible_values=None, loglevel=WARNING):
        super(GWConfigSettingWarning, self).__init__(
            key, attempted_value, *args, context="a configuration setting", possible_values=possible_values, loglevel=loglevel
        )


# ############################################################################
#                                                             ValueError-based
# ############################################################################

class GWValueError(ValueError, GWException):
    """
    Exception raised because of a bad value.

    TIP: In your try/except code, it's suggested to catch `ValueError`, in
    general, rather than `GWValueError`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.exitcode = EX_USAGE


# ############################################################################
#                                                            LookupError-based
# ############################################################################

class GWIndexError(IndexError, GWException):
    """
    Exception raised because of a bad index.

    TIP: In your try/except code, it's suggested to catch `IndexError`, in
    general rather than `GWIndexError`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super(Exception, self).__init__(*args, loglevel=loglevel)
        self.exitcode = EX_USAGE


# ############################################################################
#                                                                OSError-based
# ############################################################################

class GWFileNotFoundError(FileNotFoundError, GWException):
    """
    TIP: In your try/except code, it's suggested to catch `FileNotFoundError`,
    in general, rather than `GWFileNotFoundError`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel=loglevel)


class GWFileExistsError(FileExistsError, GWException):
    """
    TIP: In your try/except code, it's suggested to catch `FileExistsError`,
    in general, rather than `GWFileExistsError`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel=loglevel)


class GWNotADirectoryError(NotADirectoryError, GWException):
    """
    TIP: In your try/except code, it's suggested to catch `NotADirectoryError`,
    in general, rather than `GWNotADirectoryError`, specifically.

    :param args: A payload for the exception, as usual (typically either a str
    with an explanation of the error, or another instance of `Exception`).

    :param loglevel: (optional) How this error should appear in the log (if no
    outer code catches it and handles it, that is). The default is `logging.ERROR`.
    """

    def __init__(self, *args, loglevel=ERROR) -> None:
        super().__init__(*args, loglevel=loglevel)



