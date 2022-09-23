from gwpycore import TRACE, setup_enhanced_logging, config_logger, random_token

LOGGING_CONFIG = {"log_file": None, "log_level": TRACE, "no_color": True}

__all__ = [
    "logger_for_testing",
    "grab_captured_text",
]


def logger_for_testing():
    name = random_token()
    setup_enhanced_logging()
    return config_logger(name, LOGGING_CONFIG)


def grab_captured_text(captured):
    return captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
