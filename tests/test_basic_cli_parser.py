from gwpycore.gw_logging import INFO, DIAGNOSTIC, DEBUG, TRACE
from gwpycore.gw_cli import  basic_cli_parser
from argparse import ArgumentParser

def test_basic_cli_parser_no_args_minimal():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args([])
    assert switches.loglevel == INFO
    assert not switches.nocolor

def test_basic_cli_parser_no_args_all():
    p: ArgumentParser = basic_cli_parser(devel=True, trace=True, configfile=True, logfile=True, infile=True, outfile=True)
    switches = p.parse_args([])
    assert switches.loglevel == INFO
    assert not switches.nocolor
    assert not switches.devmode
    assert switches.configfile == ""
    assert switches.logfile == ""
    assert switches.infile == ""
    assert switches.outfile == ""


def test_basic_cli_parser_verbose():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args(["-v"])
    assert switches.loglevel == DIAGNOSTIC

def test_basic_cli_parser_very_verbose():
    p: ArgumentParser = basic_cli_parser()
    switches = p.parse_args(["--very-verbose"])
    assert switches.loglevel == DEBUG


def test_basic_cli_parser_trace():
    p: ArgumentParser = basic_cli_parser(trace=True)
    switches = p.parse_args(["--trace"])
    assert switches.loglevel == TRACE

def test_basic_cli_parser_files():
    p: ArgumentParser = basic_cli_parser(configfile=True, logfile=True, infile=True, outfile=True)
    switches = p.parse_args(["-c", "myapp.cfg", "-l", "myapp.log", "-i", "in.txt", "-o", "out.txt"])
    assert switches.configfile == "myapp.cfg"
    assert switches.logfile == "myapp.log"
    assert switches.infile == "in.txt"
    assert switches.outfile == "out.txt"



