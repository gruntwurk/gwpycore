from argparse import ArgumentParser

from gwpycore import DEBUG, DIAGNOSTIC, INFO, TRACE
from gwpycore import basic_cli_parser


def test_basic_cli_parser_no_args_minimal():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args([])
    assert switches.log_level == INFO
    assert not switches.no_color


def test_basic_cli_parser_no_args_all():
    p: ArgumentParser = basic_cli_parser(devel=True, trace=True, config_file=True, log_file=True, in_file=True, out_file=True)
    switches = p.parse_args([])
    assert switches.log_level == INFO
    assert not switches.no_color
    assert not switches.dev_mode
    assert switches.config_file == ""
    assert switches.log_file == ""
    assert switches.in_file == ""
    assert switches.out_file == ""


def test_basic_cli_parser_verbose():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args(["-v"])
    assert switches.log_level == DIAGNOSTIC


def test_basic_cli_parser_very_verbose():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args(["--very-verbose"])
    assert switches.log_level == DEBUG


def test_basic_cli_parser_trace():
    p: ArgumentParser = basic_cli_parser(trace=True)
    switches = p.parse_args(["--trace"])
    assert switches.log_level == TRACE


def test_basic_cli_parser_files():
    p: ArgumentParser = basic_cli_parser(config_file=True, log_file=True, in_file=True, out_file=True)
    switches = p.parse_args(["-c", "myapp.cfg", "-l", "myapp.log", "-i", "in.txt", "-o", "out.txt"])
    assert switches.config_file == "myapp.cfg"
    assert switches.log_file == "myapp.log"
    assert switches.in_file == "in.txt"
    assert switches.out_file == "out.txt"
