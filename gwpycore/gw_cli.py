from argparse import ArgumentParser

from gwpycore.gw_logging import DEBUG, DIAGNOSTIC, INFO, TRACE


def basic_cli_parser(version_text: str = "", verbose=True, very_verbose=True, nocolor=True, devel=False, trace=False, configfile=False, logfile=False, infile=False, outfile=False) -> ArgumentParser:
    """
    Instantiates an argparse.ArgumentParser with a selection of commonly used switches.
    """
    parser = ArgumentParser(description="")
    if version_text:
        parser.add_argument("--version", action="version", version=version_text)
    if devel:
        parser.add_argument("-d", "--devel", dest="devmode", help="turns on developer mode", action="store_true", default=False)
    if verbose:
        parser.add_argument("-v", "--verbose", dest="loglevel", help="sets loglevel to DIAGNOSTIC", action="store_const", const=DIAGNOSTIC, default=INFO)
    if very_verbose:
        parser.add_argument("--vv", "--very-verbose", "--debug", dest="loglevel", help="sets loglevel to DEBUG (very verbose)", action="store_const", const=DEBUG)
    if trace:
        parser.add_argument("--trace", dest="loglevel", help="sets loglevel to TRACE (super verbose)", action="store_const", const=TRACE)
    if nocolor:
        parser.add_argument("--nocolor", dest="nocolor", help="turns off coloring the log messages that are sent to the console", action="store_true", default=False)
    if logfile:
        parser.add_argument("-l", "--logfile", dest="logfile", help="specifies the name (and path) for the log file (none by default)", default="")
    if configfile:
        parser.add_argument("-c", "--configfile", dest="configfile", help="specifies the name (and path) for the configuration file (none by default)", default="")
    if infile:
        parser.add_argument("-i", "--infile", dest="infile", help="specifies the name (and path) for the input file (rather than stdin)", default="")
    if outfile:
        parser.add_argument("-o", "--outfile", dest="outfile", help="specifies the name (and path) for the output file (rather than stdout)", default="")

    return parser
