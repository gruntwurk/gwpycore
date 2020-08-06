from gwpycore.gw_exceptions import GruntWurkError, GruntWurkConfigError, GruntWurkConfigSettingWarning
import pytest
import logging
import sys
from gwpycore.gw_logging import setup_logging, CRITICAL, ERROR, WARNING, INFO, DIAGNOSTIC, DEBUG, TRACE

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
	assert captured.err == """==START==
ERROR exception
INFO log as info
==END=="""


def test_GruntWurkConfigError(capsys):
	sys.stderr.write("==START==\n")
	log = setup_logging("test2", logfile=None, nocolor=True)
	log.exception(GruntWurkConfigError("exception"))
	log.exception(GruntWurkConfigError("log as critical", loglevel=CRITICAL))
	sys.stderr.write("==END==")
	captured = capsys.readouterr()
	assert captured.out == ""
	assert captured.err == """==START==
ERROR exception
CRITICAL log as critical
==END=="""


def test_GruntWurkConfigSettingWarning(capsys):
	sys.stderr.write("==START==\n")
	log = setup_logging("test3", logfile=None, nocolor=True)
	log.exception(GruntWurkConfigSettingWarning("[section]key","foo","bar, baz"))
	sys.stderr.write("==END==")
	captured = capsys.readouterr()
	assert captured.out == ""
	assert captured.err == """==START==
WARNING The configuration setting of [section]key = foo is invalid. Possible values are: bar, baz
==END=="""
