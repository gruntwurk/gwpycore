import logging
import sys

from gwpycore import (EX_CONFIG, EX_ERROR, GWConfigError,
                      GWConfigSettingWarning, GWError,
                      log_uncaught, setup_logging, EX_WARNING
                     )

LOGGING_CONFIG = {"log_file": None, "no_color": True}

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. with_file vs. console_only); otherwise, you'll get errors trying to write to a closed file between one test to another.


def test_uncaught_error(capsys):
    setup_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("uncaught_error")
    e = GWError("An uncaught error.")
    assert log_uncaught(e, log) == EX_ERROR
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] An uncaught error.
==END=="""


def test_uncaught_config_error(capsys):
    setup_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("uncaught_config_error")
    e = GWConfigError("An uncaught config error.")
    assert log_uncaught(e, log) == EX_CONFIG
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] An uncaught config error.
==END=="""


def test_uncaught_warning(capsys):
    setup_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("uncaught_warning")
    e = GWConfigSettingWarning("[foo]bar", "baz", "boing, bing, bang")
    assert log_uncaught(e, log) == EX_WARNING
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[WARNING] The configuration setting of [foo]bar = baz is invalid. Possible values are: boing, bing, bang
==END=="""
