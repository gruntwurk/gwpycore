import logging
from pathlib import Path
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from gwpycore import GWConfigSettingWarning


LOG = logging.getLogger("gwpy")


def load_reportlab_font(font_name, filespec: Path):
    """
    Registers the given font for use with ReportLab.

    :param font_name: The font name with which ReportLab will refer to the font
    (e.g. "Arial Narrow")

    :param filespec: The file path of the font (e.g. "C:/Windows/Fonts/arialn.ttf")

    :raises GWConfigSettingWarning: If the font file does not exist or
    otherwise cannpt be loaded.
    """
    LOG.debug(f"Registering {font_name} = {str(filespec)}")
    if filespec.exists():
        registerFont(TTFont(font_name, str(filespec)))
        LOG.debug(f"Registered {font_name} = {str(filespec)}")
    else:
        raise GWConfigSettingWarning(font_name, str(filespec))


def available_fonts():
    c = Canvas("dummy.pdf")
    return c.getAvailableFonts()


__all__ = [
    "load_reportlab_font",
    "available_fonts",
]