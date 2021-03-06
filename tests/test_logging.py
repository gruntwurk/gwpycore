import logging
import sys

from gwpycore import (
    CRITICAL, DEBUG, DIAGNOSTIC, ERROR, INFO, TRACE, WARNING, GruntWurkError,
    setup_logging)

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. with_file vs. console_only); otherwise, you'll get errors trying to write to a closed file between one test to another.


def test_setup_logging_with_file():
    setup_logging.cache_clear()
    setup_logging("with_file")
    log = logging.getLogger("nosuch")
    assert len(log.handlers) == 0
    log = logging.getLogger("with_file")
    assert len(log.handlers) >= 1


def test_setup_logging_console_only():
    setup_logging.cache_clear()
    setup_logging("console_only", logfile=None)
    log = logging.getLogger("nosuch")
    assert len(log.handlers) == 0
    log = logging.getLogger("console_only")
    assert len(log.handlers) >= 1


def test_logging_error_method(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("error_method", logfile=None, nocolor=True)
    log.error("error")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nERROR error\n==END=="


def test_logging_debug_method_quiet(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("debug_q", logfile=None, nocolor=True)
    log.debug("debug")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_debug_method_verbose(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("debug_v", loglevel=DEBUG, logfile=None, nocolor=True)
    log.debug("debug")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nDIAGNOSTIC Logging level for the console is set to DEBUG.\nDEBUG debug\n==END=="


def test_logging_diagnostic_method_quiet(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("diagnostic_q", logfile=None, nocolor=True)
    log.diagnostic("diagnostic")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_diagnostic_method_verbose(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("diagnostic_v", loglevel=DIAGNOSTIC, logfile=None, nocolor=True)
    log.diagnostic("diagnostic")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nDIAGNOSTIC Logging level for the console is set to DIAGNOSTIC.\nDIAGNOSTIC diagnostic\n==END=="


def test_logging_trace_method_quiet(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("trace_q", logfile=None, nocolor=True)
    log.trace("trace")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_trace_method_verbose(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("trace_v", loglevel=TRACE, logfile=None, nocolor=True)
    log.trace("trace")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nDIAGNOSTIC Logging level for the console is set to TRACE.\nTRACE trace\n==END=="


def test_logging_exception_method(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("exception_method", logfile=None, nocolor=True)
    log.exception(GruntWurkError("exception", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nCRITICAL exception\n==END=="


def test_logging_uncaught_method(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    setup_logging("uncaught_method", logfile=None, nocolor=True)
    log = logging.getLogger("uncaught_method")
    log.uncaught(GruntWurkError("uncaught"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\nERROR Uncaught error detected. There is no good reason why the following error wasn't handled earlier.\nERROR uncaught\n==END=="


def test_level_constants():
    assert CRITICAL == 50
    assert ERROR == 40
    assert WARNING == 30
    assert INFO == 20
    assert DIAGNOSTIC == 15
    assert DEBUG == 10
    assert TRACE == 5
    assert logging.getLevelName(DIAGNOSTIC) == "DIAGNOSTIC"
    assert logging.getLevelName(TRACE) == "TRACE"
