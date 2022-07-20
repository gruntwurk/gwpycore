import sys

from gwpycore import (CRITICAL, INFO, GruntWurkConfigError,
                      GruntWurkConfigSettingWarning, GruntWurkError, GruntWurkWarning,
                      setup_logging)

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. test_err
#    vs. test_warn); otherwise, you'll get errors trying to write to a closed
#    file between one test to another.


def test_GruntWurkError(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test_err", logfile=None, nocolor=True)
    log.exception(GruntWurkError("exception"))
    log.exception(GruntWurkError("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nERROR exception\nINFO log as info\n==END=="


def test_GruntWurkWarning(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test_warn", logfile=None, nocolor=True)
    log.exception(GruntWurkWarning("warning"))
    log.exception(GruntWurkWarning("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nWARNING warning\nINFO log as info\n==END=="


def test_GruntWurkConfigError(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test_conf_err", logfile=None, nocolor=True)
    log.exception(GruntWurkConfigError("exception"))
    log.exception(GruntWurkConfigError("log as critical", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nERROR exception\nCRITICAL log as critical\n==END=="


def test_GruntWurkConfigSettingWarning(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test_conf_warn", logfile=None, nocolor=True)
    log.exception(GruntWurkConfigSettingWarning("[section]key", "foo", "bar, baz"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nWARNING The configuration setting of [section]key = foo is invalid. Possible values are: bar, baz\n==END=="
