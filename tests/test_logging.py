import logging
import sys

from gwpycore import (CRITICAL, DEBUG, DIAGNOSTIC, ERROR, INFO, TRACE, WARNING,
                      GWError,
                      logger_for_testing, grab_captured_err_text
                      )

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g.
# with_file vs. console_only); otherwise, you'll get errors trying to write
# to a closed file between one test to another.


# def test_setup_enhanced_logging_with_file():
#     log = logging.getLogger()
#     assert len(log.handlers) == 0
#     log = logger_for_testing("with_file", {"log_file": "foo.log", "no_color": True})
#     assert len(log.handlers) == 2


# def test_setup_enhanced_logging_console_only():
#     log = logger_for_testing()
#     assert len(log.handlers) == 0
#     assert len(log.handlers) == 1


def test_logging_error_method(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    log.error("error")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
[ERROR  ] error
==END=="""


def test_logging_debug_method_quiet(capsys):
    log = logger_for_testing()
    log.setLevel(INFO)
    sys.stderr.write("==START==\n")
    log.debug("debug")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_debug_method_verbose(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
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
    log = logger_for_testing()
    log.setLevel(INFO)
    sys.stderr.write("==START==\n")
    log.diagnostic("diagnostic")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_diagnostic_method_verbose(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
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
    log = logger_for_testing()
    log.setLevel(INFO)
    sys.stderr.write("==START==\n")
    log.diagnostic('Logging level for the console is set to the default of WARNING.')
    log.trace("trace")
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "==START==\n==END=="


def test_logging_trace_method_verbose(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
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
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    log.exception(GWError("exception", loglevel=CRITICAL))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == """[CRITICAL] exception
"""


def test_logging_uncaught_method(capsys):
    log = logger_for_testing()
    sys.stderr.write("==START==\n")
    log.uncaught(GWError("uncaught"))
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == \
        """[ERROR  ] Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
[ERROR  ] uncaught
"""


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
