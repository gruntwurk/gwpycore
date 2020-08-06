from gwpycore.gw_exceptions import GruntWurkConfigError, GruntWurkConfigSettingWarning, GruntWurkError, EX_ERROR, EX_CONFIG, EX_OK
import sys
from gwpycore.gw_logging import log_uncaught, setup_logging

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. with_file vs. console_only); otherwise, you'll get errors trying to write to a closed file between one test to another.


def test_uncaught_error(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("uncaught_error", logfile=None, nocolor=True)
    e = GruntWurkError("An uncaught error.")
    assert log_uncaught(log, e) == EX_ERROR
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
ERROR Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
ERROR An uncaught error.
==END=="""

def test_uncaught_config_error(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("uncaught_config_error", logfile=None, nocolor=True)
    e = GruntWurkConfigError("An uncaught config error.")
    assert log_uncaught(log, e) == EX_CONFIG
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
ERROR Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
ERROR An uncaught config error.
==END=="""

def test_uncaught_warning(capsys):
    setup_logging.cache_clear()
    sys.stderr.write("==START==\n")
    log = setup_logging("uncaught_warning", logfile=None, nocolor=True)
    e = GruntWurkConfigSettingWarning("[foo]bar","baz","boing, bing, bang")
    assert log_uncaught(log, e) == EX_OK
    sys.stderr.write("==END==")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == """==START==
ERROR Uncaught error detected. There is no good reason why the following error wasn't handled earlier.
WARNING The configuration setting of [foo]bar = baz is invalid. Possible values are: boing, bing, bang
==END=="""

