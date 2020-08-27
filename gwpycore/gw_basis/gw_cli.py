from argparse import ArgumentParser

from .gw_logging import DEBUG, DIAGNOSTIC, INFO, TRACE


def basic_cli_parser(
    version_text="", verbose=True, very_verbose=True, nocolor=True, filenames="", devel=False, trace=False, configfile=False, configfile_default="", logfile=False, logfile_default="", infile=False, outfile=False, recurse=False
) -> ArgumentParser:
    """
    Instantiates an argparse.ArgumentParser with a selection of commonly used switches.

    Arguments:
        (booleans) -- whether or not to include a switch for that option
        filenames -- how many file names may follow the last switch (filenames=3, filenames="*", filenames="+", filenames="?")
                    (specific number, zero or more, one or more, zero or one, respectively)
    """
    parser = ArgumentParser(description="")
    if version_text:
        parser.add_argument("--version", action="version", version=version_text)
    if filenames:
        parser.add_argument("filenames", nargs=filenames, help="one or more files to be processed")
    if devel:
        parser.add_argument("-d", "--devel", dest="devmode", help="turns on developer mode", action="store_true", default=False)
    if verbose:
        parser.add_argument("-v", "--verbose", dest="loglevel", help="prints informative messages", action="store_const", const=DIAGNOSTIC, default=INFO)
    if very_verbose:
        parser.add_argument("--vv", "--very-verbose", "--debug", dest="loglevel", help="prints detailed (debugging) messages", action="store_const", const=DEBUG)
    if trace:
        parser.add_argument("--trace", dest="loglevel", help="prints super-verbose (debugging and tracing) messages", action="store_const", const=TRACE)
    if nocolor:
        parser.add_argument("--nocolor", dest="nocolor", help="turns off coloring the log messages that are sent to the console", action="store_true", default=False)
    if logfile or logfile_default:
        parser.add_argument("-l", "--logfile", dest="logfile", help=f"specifies the name (and path) for the log file (({logfile_default if logfile_default else 'None'} by default)", default=logfile_default)
    if configfile or configfile_default:
        parser.add_argument("-c", "--configfile", dest="configfile", help=f"specifies the name (and path) for the configuration file ({configfile_default if configfile_default else 'None'} by default)", default=configfile_default)
    if infile:
        parser.add_argument("-i", "--infile", dest="infile", help="specifies the name (and path) for the input file (rather than stdin)", default="")
    if outfile:
        parser.add_argument("-o", "--outfile", dest="outfile", help="specifies the name (and path) for the output file (rather than stdout)", default="")
    if recurse:
        parser.add_argument("-r", "--recurse", dest="recurse", help="searches in subdirectories as well", action="store_true", default=False)

    return parser


_all__ = "basic_cli_parser"
