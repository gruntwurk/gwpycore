import re
import sys
from gwpycore import TRACE, setup_enhanced_logging, config_logger, random_token

LOGGING_CONFIG = {"log_file": None, "log_level": TRACE, "no_color": True}

__all__ = [
    "logger_for_testing",
    "grab_captured_err_text",
    "stderr_start_marker",
    "stderr_end_marker",
]


START_MARKER = "==START==\n"
END_MARKER = "==END=="


def logger_for_testing():
    name = random_token()
    setup_enhanced_logging()
    return config_logger(name, LOGGING_CONFIG)


def grab_captured_err_text(captured):
    text = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    return text.replace(START_MARKER, '').replace(END_MARKER, '')


def stderr_start_marker():
    sys.stderr.write(START_MARKER)


def stderr_end_marker():
    sys.stderr.write(END_MARKER)