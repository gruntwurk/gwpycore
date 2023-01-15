import logging
import re
from pathlib import Path
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from gwpycore import GWConfigSettingWarning

__all__ = [
    "load_reportlab_font",
    "available_fonts",
]

LOG = logging.getLogger("gwpy")


def load_reportlab_font(font_name, filespec: Path):
    """
    Registers the given font for use with ReportLab. In the particular case of
    a font that ends in `Regular`, `Bold`, `Italic`, or `Bold Italic`, it also
    maps that font to the corresponding combination of <b> and/or <i> markup tags
    (for use within a Paragraph flowable).

    :param font_name: The font name with which ReportLab will refer to the font
    (e.g. "Arial Narrow"). FYI: This name is internally refered to as the
    postscript font name, i.e. `psname`.

    :param filespec: The file path of the font (e.g. "C:/Windows/Fonts/arialn.ttf")

    :raises GWConfigSettingWarning: If the font file does not exist or
    otherwise cannpt be loaded.
    """
    # LOG.debug(f"Registering {font_name} = {str(filespec)}")
    if not filespec.exists():
        raise GWConfigSettingWarning(font_name, str(filespec))

    registerFont(TTFont(font_name, str(filespec)))

    if m := re.match(r'(.*)[- ](Regular|BoldItalic|BoldOblique|Bold|Italic|Oblique)$', font_name):
        family = m[1]
        variant = m[2].replace('Oblique', 'Italic')
        is_bold = 'Bold' in variant
        is_italic = 'Italic' in variant
        addMapping(family, 1 if is_bold else 0, 1 if is_italic else 0, font_name)
    # LOG.debug(f"Registered {font_name} = {str(filespec)}")


def available_fonts():
    c = Canvas("dummy.pdf")
    return c.getAvailableFonts()
