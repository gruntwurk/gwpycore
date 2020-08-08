import logging
import sys

import pytest

from gwpycore.gw_exceptions import (GruntWurkConfigError,
                                    GruntWurkConfigSettingWarning,
                                    GruntWurkError)
from gwpycore.gw_logging import (CRITICAL, DEBUG, DIAGNOSTIC, ERROR, INFO,
                                 TRACE, WARNING, setup_logging)

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. test1 vs. test2); otherwise, you'll get errors trying to write to a closed file between one test to another.


def test_GruntWurkError(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test1", logfile=None, nocolor=True)
    log.exception(GruntWurkError("exception"))
    log.exception(GruntWurkError("log as info", loglevel=INFO))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
	assert (captured.err == "==START==\nERROR exception\nINFO log as info\n==END=="


def test_GruntWurkConfigError(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test2", logfile=None, nocolor=True)
    log.exception(GruntWurkConfigError("exception"))
    log.exception(GruntWurkConfigError("log as critical", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nERROR exception\nCRITICAL log as critical\n==END=="



def test_GruntWurkConfigSettingWarning(capsys):
    sys.stderr.write("==START==\n")
    log = setup_logging("test3", logfile=None, nocolor=True)
    log.exception(GruntWurkConfigSettingWarning("[section]key", "foo", "bar, baz"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nWARNING The configuration setting of [section]key = foo is invalid. Possible values are: bar, baz\n==END=="

