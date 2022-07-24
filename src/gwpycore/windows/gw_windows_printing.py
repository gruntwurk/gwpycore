import logging
from typing import List, Union
from pathlib import Path

import win32api
import win32print

LOG = logging.getLogger("main")

SIMPLEX = 1  # no flip
DUPLEX_LONG_EDGE = 2  # flip up
DUPLEX_SHORT_EDGE = 3  # flip over


# ShellExecute args:
# 1. The handle of the parent window, or 0 for no parent.
# 2. The operation to be performed. A verb appropriate for the file (e.g. "open", "print"), or None
# 3. The name of the file to open/execute (a document or an executable).
# 4. The parameters to pass, if the file name contains an executable. Should be None for a document file.
# 5. The initial directory for the application.
# 6. Specifies whether the application is shown when it is opened (if the app cares to take this hint).
#   0 = Open the application with a hidden window. (Always use 0 for a document.)
#   1 = Open the application with a normal window. If the window is minimized or maximized, the system restores it to its original size and position.
#   2 = Open the application with a minimized window.
#   3 = Open the application with a maximized window.
#   4 = Open the application with its window at its most recent size and position. The active window remains active.
#   5 = Open the application with its window at its current size and position.
#   7 = Open the application with a minimized window. The active window remains active.
#   10 = Open the application with its window in the default state specified by the application.

def available_printers() -> List:
    """
    Returns a list of the printers that are (currently) available for printing.

    :return: A list of printers by their human-readable names.
    """
    return [printer[2] for printer in win32print.EnumPrinters(2)]


def view_pdf(pdf_filename: Union[Path,str]):
    """
    Opens the given PDF document (using the operating system's default program).

    :param pdf_filename: Qualified filename of the PDF file to open.
    """
    win32api.ShellExecute(0, "open", str(pdf_filename), "", ".", 0)


def print_pdf(pdf_filename: Union[Path, str], printer="default", duplex=SIMPLEX, color=True, copies = 1):
    """
    Sends the given PDF document to the printer.

    :param pdf_filename: Qualified filename of the PDF file to print.

    :param printer: Which printer to use. Defaults to "default".

    :param duplex: Whether or not to print on both sides of the paper. Defaults to SIMPLEX.

    :param color: Whether or not to print in color (if possible). Defaults to True.

    :param copies: The number of copies to print. Defaults to 1.
    """
    if printer == "default":
        printer = win32print.GetDefaultPrinter()
    PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
    p_handle = win32print.OpenPrinter(printer, PRINTER_DEFAULTS)
    properties = win32print.GetPrinter(p_handle, 2)
    properties['pDevMode'].Color = 1 if color else 0
    properties['pDevMode'].Copies = copies
    properties['pDevMode'].Duplex = duplex
    win32print.SetPrinter(p_handle, 2, properties, 0)
    win32api.ShellExecute(0, "print", str(pdf_filename), '/d:"%s"' % printer, ".", 0)


__all__ = [
    "available_printers",
    "view_pdf",
    "print_pdf",
]
