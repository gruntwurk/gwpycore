import logging

import win32api
import win32print

LOG = logging.getLogger("main")

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


def view_pdf(pdfName: str):
    win32api.ShellExecute(0, "open", pdfName, "", ".", 0)


def print_pdf(pdfName: str, printer="default"):
    if printer == "default":
        printer = win32print.GetDefaultPrinter()
    win32api.ShellExecute(0, "print", pdfName, '/d:"%s"' % printer, ".", 0)


__all__ = ("view_pdf", "print_pdf")
