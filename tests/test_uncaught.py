import sys

from gwpycore import (EX_CONFIG, EX_ERROR, EX_WARNING,
                      TRACE,
                      GWError, GWConfigError,
                      GWConfigSettingWarning,
                      log_uncaught,
                      logger_for_testing,
                      grab_captured_text
                      )

LOGGING_CONFIG = {"log_file": None, "log_level": TRACE, "no_color": True}

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. with_file vs. console_only); otherwise, you'll get errors trying to write to a closed file between one test to another.


def test_uncaught_error(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    e = GWError("An uncaught error.")
    assert log_uncaught(e, log) == EX_ERROR
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] An uncaught error.
==END=="""


def test_uncaught_config_error(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    e = GWConfigError("An uncaught config error.")
    assert log_uncaught(e, log) == EX_CONFIG
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] An uncaught config error.
==END=="""


def test_uncaught_warning(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    e = GWConfigSettingWarning("[foo]bar", "baz", possible_values="boing, bing, bang")
    assert log_uncaught(e, log) == EX_WARNING
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[WARNING] The configuration setting of [foo]bar = baz is invalid. Possible values are: boing, bing, bang
==END=="""
