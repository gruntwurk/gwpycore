import logging
import sys

from gwpycore import (
    CRITICAL, DEBUG, DIAGNOSTIC, ERROR, INFO, TRACE, WARNING, GWError,
    setup_enhanced_logging)
from gwpycore.core.gw_logging import config_logger


LOGGING_CONFIG = {"log_file": None, "no_color": True}

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g.
# with_file vs. console_only); otherwise, you'll get errors trying to write
# to a closed file between one test to another.


def test_setup_enhanced_logging_with_file():
    setup_enhanced_logging(LOGGING_CONFIG)
    log = logging.getLogger("nosuch")
    assert len(log.handlers) == 0
    log = config_logger("with_file", {"log_file": "foo.log", "no_color": True})
    assert len(log.handlers) == 2


def test_setup_enhanced_logging_console_only():
    setup_enhanced_logging()
    log = logging.getLogger("nosuch")
    assert len(log.handlers) == 0
    log = config_logger("console_only", LOGGING_CONFIG)
    assert len(log.handlers) == 1


def test_logging_error_method(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)
    sys.stderr.write("==START==\n")
    log = logging.getLogger("error_method")
    log.error("error")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
[ERROR  ] error
==END=="""


def test_logging_debug_method_quiet(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = logging.getLogger("debug_q")
    log.debug("debug")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_debug_method_verbose(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = config_logger("debug_v", {"log_level": DEBUG, "log_file": None, "no_color": True})
    log.diagnostic('Logging level for the console is set to DEBUG.')
    log.debug("debug")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
[DIAGNOSTIC] Logging level for the console is set to DEBUG.
[DEBUG  ] debug
==END=="""


def test_logging_diagnostic_method_quiet(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = logging.getLogger("diagnostic_q")
    log.diagnostic("diagnostic")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_diagnostic_method_verbose(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = config_logger("diagnostic_v", {"log_level": DIAGNOSTIC, "log_file": None, "no_color": True})
    log.diagnostic('Logging level for the console is set to DIAGNOSTIC.')
    log.diagnostic("diagnostic")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
[DIAGNOSTIC] Logging level for the console is set to DIAGNOSTIC.
[DIAGNOSTIC] diagnostic
==END=="""


def test_logging_trace_method_quiet(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = logging.getLogger("trace_q")
    log.diagnostic('Logging level for the console is set to the default of WARNING.')
    log.trace("trace")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_trace_method_verbose(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = config_logger("trace_v", {"log_level": TRACE, "log_file": None, "no_color": True})
    log.diagnostic('Logging level for the console is set to TRACE.')
    log.trace("trace")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
[DIAGNOSTIC] Logging level for the console is set to TRACE.
[TRACE  ] trace
==END=="""


def test_logging_exception_method(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = logging.getLogger("exception_method")
    log.exception(GWError("exception", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == """==START==
[CRITICAL] exception
==END=="""


def test_logging_uncaught_method(capsys):
    setup_enhanced_logging(LOGGING_CONFIG)

    sys.stderr.write("==START==\n")
    log = logging.getLogger("uncaught_method")
    log.uncaught(GWError("uncaught"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = captured.err.replace('NoneType: None\n', '')  # FIXME Why in the hell is this necessary????????????
    assert err_txt == \
        """==START==
[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] uncaught
==END=="""


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
