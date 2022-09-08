import sys
import logging

from gwpycore import (CRITICAL, INFO, GWConfigError,
                      GWConfigSettingWarning, GWError, GWWarning,
                      setup_enhanced_logging, config_logger,
                      )

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. test_err
#    vs. test_warn); otherwise, you'll get errors trying to write to a closed
#    file between one test to another.

LOGGING_CONFIG = {"log_file": None, "no_color": True}


def test_GruntWurkError(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("test_error")
    log.exception(GWError("exception"))
    log.exception(GWError("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == "==START==\n[ERROR  ] exception\n[INFO   ] log as info\n==END=="


def test_GruntWurkWarning(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("test_warn", )
    log.exception(GWWarning("warning"))
    log.exception(GWWarning("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == "==START==\n[WARNING] warning\n[INFO   ] log as info\n==END=="


def test_GruntWurkConfigError(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("test_conf_err")
    log.exception(GWConfigError("exception"))
    log.exception(GWConfigError("log as critical", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == "==START==\n[ERROR  ] exception\n[CRITICAL] log as critical\n==END=="


def test_GruntWurkConfigSettingWarning(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("test_conf_warn")
    log.exception(GWConfigSettingWarning("[section]key", "foo", "bar, baz"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == "==START==\n[WARNING] The configuration setting of [section]key = foo is invalid. Possible values are: bar, baz\n==END=="
