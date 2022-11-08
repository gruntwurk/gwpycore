from gwpycore import (CRITICAL, INFO, GWConfigError,
                      GWConfigSettingWarning, GWError, GWWarning,
                      logger_for_testing, grab_captured_err_text,
                      stderr_start_marker, stderr_end_marker
                      )

# Notes:
# 1. The capsys fixture captures sys.stdout and sys.stderr for us
# 2. It's important that every test uses a different logger name (e.g. test_err
#    vs. test_warn); otherwise, you'll get errors trying to write to a closed
#    file between one test to another.


def test_GWError(capsys):
    log = logger_for_testing()
    stderr_start_marker()
    log.exception(GWError("exception"))
    log.exception(GWError("log as info", loglevel=INFO))
    stderr_end_marker()
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == "[ERROR  ] exception\n[INFO   ] log as info\n"


def test_GWWarning(capsys):
    log = logger_for_testing()
    stderr_start_marker()
    log.exception(GWWarning("warning"))
    log.exception(GWWarning("log as info", loglevel=INFO))
    stderr_end_marker()
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == "[WARNING] warning\n[INFO   ] log as info\n"


def test_GWConfigError(capsys):
    log = logger_for_testing()

    stderr_start_marker()
    log.exception(GWConfigError("exception"))
    log.exception(GWConfigError("log as critical", loglevel=CRITICAL))
    stderr_end_marker()
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == "[ERROR  ] exception\n[CRITICAL] log as critical\n"


def test_GWConfigSettingWarning(capsys):
    log = logger_for_testing()

    stderr_start_marker()
    log.exception(GWConfigSettingWarning("[section]key", "foo", possible_values="bar, baz"))
    stderr_end_marker()
    captured = capsys.readouterr()
    assert captured.out == ""
    err_txt = grab_captured_err_text(captured)
    assert err_txt == "[WARNING] In a configuration setting, [section]key = foo is invalid. Possible values are: bar, baz\n"
