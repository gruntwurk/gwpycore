#! /usr/bin/env python

# This example is a rewrite of code that was originally released to the
# public domain by Tim Peters, 03 October 2000:
# http://svn.python.org/projects/python/trunk/Tools/scripts/reindent.py

"""reindent [-d][-r][-v] [ path ... ]

-d (--dryrun)   Dry run.   Analyze, but don't make any changes to, files.
-r (--recurse)  Recurse.   Search for all .py files in subdirectories too.
-n (--nobackup) No backup. Does not make a ".bak" file before reindenting.
-v (--verbose)  Verbose.   Print informative msgs; else no output.
-h (--help)     Help.      Print this usage information and exit.

Change Python (.py) files to use 4-space indents and no hard tab characters.
Also trim excess spaces and tabs from ends of lines, and remove empty lines
at the end of files. Also ensure the last line ends with a newline.

If no paths are given on the command line, reindent operates as a filter,
reading a single source file from standard input and writing the transformed
source to standard output.  In this case, the -d, -r and -v flags are
ignored.

You can pass one or more file and/or directory paths.  When a directory
path, all .py files within the directory will be examined, and, if the -r
option is given, likewise recursively for subdirectories.

If output is not to standard output, reindent overwrites files in place,
renaming the originals with a .bak extension.  If it finds nothing to
change, the file is left alone.  If reindent does change a file, the changed
file is a fixed-point for future runs (i.e., running reindent on the
resulting .py file won't change it again).

The hard part of reindenting is figuring out what to do with comment
lines.  So long as the input files get a clean bill of health from
tabnanny.py, reindent should do a good job.

The backup file is a copy of the one that is being reindented. The ".bak"
file is generated with shutil.copy(), but some corner cases regarding
user/group and permissions could leave the backup file more readable that
you'd prefer. You can always use the --nobackup option to prevent this.
"""

__version__ = "2"

import argparse
from logging import Logger
import os
import shutil
import sys
import tokenize
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from gwpycore import (basic_cli_parser, leading_spaces_count, rstrip_special,
                      setup_logging)

CONFIG: argparse.Namespace
LOG: Logger


def load_command_line():
    p: ArgumentParser = basic_cli_parser(__version__, filenames="*", verbose=True, recurse=True, logfile=True)
    p.add_argument("-d", "--dryrun", dest="dryrun", help="Analyze, but don't make any changes to, files.", action="store_true", default=False)
    p.add_argument("-n", "--nobackup", dest="makebackup", help='Does not make a ".bak" file before reindenting.', action="store_false", default=True)
    global CONFIG
    CONFIG = p.parse_args()


def main():
    load_command_line()

    logfilepath: Optional[Path] = Path(CONFIG.logfile) if CONFIG.logfile else None
    global LOG
    LOG = setup_logging("main", loglevel=CONFIG.loglevel, logfile=logfilepath, nocolor=CONFIG.nocolor)

    if not CONFIG.filenames:
        # no filenames given on the command line, so use stdin
        r = Reindenter(sys.stdin)
        r.run()
        r.write(sys.stdout)
        return
    for filename in CONFIG.filenames:
        check(filename)


def check(file_spec):
    if os.path.isdir(file_spec) and not os.path.islink(file_spec):
        directory = file_spec
        LOG.diagnostic("Searching directory: {directory}")
        names = os.listdir(directory)
        for name in names:
            fullname = os.path.join(directory, name)
            if fullname.lower().endswith(".py"):
                check(fullname)
            elif CONFIG.recurse and os.path.isdir(fullname) and not os.path.islink(fullname) and not os.path.split(fullname)[1].startswith("."):
                check(fullname)
        return

    LOG.trace("checking {file_spec} ...")

    with Path(file_spec).open("r") as f:
        try:
            r = Reindenter(f)
        except IOError as e:
            LOG.error(f"{file_spec}: I/O Error: {e.msg}")
            return

    tabs_altered = r.run()
    if tabs_altered:
        if CONFIG.dryrun:
            LOG.diagnostic("{file_spec} would have changed, but this is a dry run.")
        else:
            if CONFIG.makebackup:
                bak = file_spec + ".bak"
                shutil.copyfile(file_spec, bak)
                LOG.diagnostic(f"backed up {file_spec} to {bak}")
            with Path(file_spec).open("w") as f:
                r.write(f)
                LOG.diagnostic("wrote new {file_spec}")
        return True
    else:
        LOG.diagnostic("{file_spec} unchanged.")
        return False


class Reindenter:
    def __init__(self, f):
        """
        Constructs an instance and loads the contents of the file into memory.
        """
        self.find_stmt = 1  # next token begins a fresh stmt?
        self.level = 0  # current indent level

        # Raw file lines.
        self.raw = f.readlines()

        # File lines, rstripped & tab-expanded.  Dummy at start is so
        # that we can use tokenize's 1-based line numbering easily.
        # Note that a line is all-blank iff it's "\n".
        self.lines = [rstrip_special(line).expandtabs() + "\n" for line in self.raw]
        self.lines.insert(0, None)
        self.index = 1  # index into self.lines of next line

        # List of (lineno, indentlevel) pairs, one for each stmt and
        # comment line.  indentlevel is -1 for comment lines, as a
        # signal that tokenize doesn't know what to do about them;
        # indeed, they're our headache!
        self.stats = []

    def run(self):
        """
        Does the analysis/conversion, still in memory.
        """
        tok_gen = tokenize.tokenize(self._getline)

        for tok_type, token, (sline, scol), end, line in tok_gen:
            self._tokeneater(tok_type, token, sline, scol, end, line)

        # Remove trailing empty lines.
        lines = self.lines
        while lines and lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line with *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        for i in range(len(stats) - 1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i + 1][0]
            have = leading_spaces_count(lines[thisstmt])
            want = thislevel * 4
            if want < 0:
                # A comment line.
                if have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    if want < 0:
                        # Then it probably belongs to the next real stmt.
                        for j in range(i + 1, len(stats) - 1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                if have == leading_spaces_count(lines[jline]):
                                    want = jlevel * 4
                                break
                    if want < 0:  # Maybe it's a hanging
                        # comment like this one,
                        # in which case we should shift it like its base
                        # line got shifted.
                        for j in range(i - 1, -1, -1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                want = have + leading_spaces_count(after[jline - 1]) - leading_spaces_count(lines[jline])
                                break
                    if want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                else:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            if diff == 0 or have == 0:
                after.extend(lines[thisstmt:nextstmt])
            else:
                for line in lines[thisstmt:nextstmt]:
                    if diff > 0:
                        if line == "\n":
                            after.append(line)
                        else:
                            after.append(" " * diff + line)
                    else:
                        remove = min(leading_spaces_count(line), -diff)
                        after.append(line[remove:])
        return self.raw != self.after

    def write(self, f):
        """
        Writes the converted text to disk.
        """
        f.writelines(self.after)

    # Line-getter for tokenize.
    def _getline(self):
        if self.index >= len(self.lines):
            line = ""
        else:
            line = self.lines[self.index]
            self.index += 1
        return line

    # Line-eater for tokenize.
    def _tokeneater(self, tok_type, token, sline, scol, end, line, INDENT=tokenize.INDENT, DEDENT=tokenize.DEDENT, NEWLINE=tokenize.NEWLINE, COMMENT=tokenize.COMMENT, NL=tokenize.NL):

        if tok_type == NEWLINE:
            # A program statement, or ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        elif tok_type == INDENT:
            self.find_stmt = 1
            self.level += 1

        elif tok_type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        elif tok_type == COMMENT:
            if self.find_stmt:
                self.stats.append((sline, -1))
                # but we're still looking for a new stmt, so leave
                # find_stmt alone

        elif tok_type == NL:
            pass

        elif self.find_stmt:
            # This is the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, or an
            # ENDMARKER.
            self.find_stmt = 0
            if line:  # not endmarker
                self.stats.append((sline, self.level))


if __name__ == "__main__":
    main()
