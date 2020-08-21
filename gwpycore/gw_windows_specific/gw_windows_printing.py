import win32api, win32print

def printPdf(pdfName: str, printer="default"):
    if printer == "default":
        printer = win32print.GetDefaultPrinter()
    win32api.ShellExecute(0, "print", pdfName, '/d:"%s"' % printer, ".", 0)

__all__ = ("printPdf",)
