import sys
# import logging

from gwpycore import (CRITICAL, INFO, GWConfigError,
                      GWConfigSettingWarning, GWError, GWWarning,
                      logger_for_testing, grab_captured_text
                      )

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. test_err
#    vs. test_warn); otherwise, you'll get errors trying to write to a closed
#    file between one test to another.


def test_GWError(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    log.exception(GWError("exception"))
    log.exception(GWError("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == "==START==\n[ERROR  ] exception\n[INFO   ] log as info\n==END=="


def test_GWWarning(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    log.exception(GWWarning("warning"))
    log.exception(GWWarning("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == "==START==\n[WARNING] warning\n[INFO   ] log as info\n==END=="


def test_GWConfigError(capsys):
    log = logger_for_testing()

    sys.stderr.write("==START==\n")
    log.exception(GWConfigError("exception"))
    log.exception(GWConfigError("log as critical", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == "==START==\n[ERROR  ] exception\n[CRITICAL] log as critical\n==END=="


def test_GWConfigSettingWarning(capsys):
    log = logger_for_testing()

    sys.stderr.write("==START==\n")
    log.exception(GWConfigSettingWarning("[section]key", "foo", possible_values="bar, baz"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_text(captured)
    assert err_txt == "==START==\n[WARNING] The configuration setting of [section]key = foo is invalid. Possible values are: bar, baz\n==END=="
