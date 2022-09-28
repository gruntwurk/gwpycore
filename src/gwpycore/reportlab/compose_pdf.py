from pathlib import Path
from typing import Union
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.pathobject import PDFPathObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER

from gwpycore import GWError, GlobalSettings
from gwpycore import NamedColor
import logging

__all__ = [
    "PDFRepresentation",
]

LOG = logging.getLogger("gwpy")
CONFIG = GlobalSettings()

DEFAULT_MARGIN = 3  # pt
DEFAULT_COLOR = NamedColor.BLACK.float_tuple()
DEFAULT_FONT_HEIGHT = 10  # pt
DEFAULT_MIN_VERTICAL_SPACING = 2  # pt


class PDFRepresentation():
    def __init__(self, folder: Union[Path, str], pagesize=LETTER, filename: str = "document.pdf") -> None:
        self.folder = folder
        self.filename = filename
        self._min_vertical_spacing = DEFAULT_MIN_VERTICAL_SPACING
        self.c = Canvas(self.full_filename(), pagesize)

        # page specs
        # LOG.debug(pagesize)
        self.right_edge, self.top_edge = pagesize
        self.center_line = self.right_edge / 2
        self.top_margin = self.bottom_margin = DEFAULT_MARGIN - 2
        self.left_margin = self.right_margin = DEFAULT_MARGIN
        self.body_width = self.right_edge - self.left_margin - self.right_margin
        self.vert_pos = self.top_edge - self.top_margin

    @property
    def min_vertical_spacing(self):
        """The min_vertical_spacing property."""
        return self._min_vertical_spacing

    @min_vertical_spacing.setter
    def min_vertical_spacing(self, value):
        self._min_vertical_spacing = value

    def full_filename(self) -> str:
        pdf_dir_path = Path(self.folder)
        pdf_dir_path.mkdir(exist_ok=True)
        return str(pdf_dir_path / self.filename)

    def finalize(self) -> str:
        try:
            self.c.save()
        except PermissionError:
            raise GWError(f"Cannot overwrite {self.c._filename} while it is in use.")
        LOG.debug(f"{self.c._filename} saved.")
        return self.c._filename

    def new_page(self):
        self.c.showPage()
        self.vert_pos = self.top_edge - self.top_margin

    def rectangle(self, x, y, w, h) -> PDFPathObject:
        p = self.c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + w, y)
        actual_height = h - 1
        if actual_height > 0:
            p.lineTo(x + w, y - actual_height)
            p.lineTo(x, y - actual_height)
            p.lineTo(x, y)
        p.close()
        return p

    def background_shading(self, background_color, height):
        '''
        Draw background shading across the full width of the badge, starting
        at the current vertical position and going down for the epcified height.
        '''
        # This does not advance the vert_pos
        # Ignoring the page margins on purpose
        width = self.right_edge
        y = self.vert_pos
        p = self.rectangle(0, y, width, height)
        self.c.setFillColor(background_color)
        self.c.setStrokeColor(background_color)
        self.c.drawPath(p, stroke=1, fill=1)

    def centered_divider(self, color, length=0.8, thickness=1):
        divider_length = int(self.right_edge * length)
        divider_start = int((self.right_edge - divider_length) / 2)
        p = self.rectangle(divider_start, self.vert_pos, divider_length, thickness)
        self.c.setFillColor(color)
        self.c.setStrokeColor(color)
        self.c.setLineWidth(1)
        self.c.drawPath(p, stroke=1, fill=1)
        self.vert_pos -= thickness + DEFAULT_MIN_VERTICAL_SPACING

    def centered_text(self, text: str, font_name, color, border_color=None,
                      font_height=DEFAULT_FONT_HEIGHT, space_below=DEFAULT_MIN_VERTICAL_SPACING
                      ):
        self.c.setFont(font_name, font_height)
        self.c.setFillColor(color)
        padding = 0
        if border_color:
            padding = 2
            p = self.rectangle(self.left_margin, self.vert_pos + padding, self.body_width, font_height + 4 + padding * 2)
            self.c.setStrokeColor(border_color)
            self.c.drawPath(p, stroke=1, fill=0)
        self.vert_pos -= font_height
        self.c.drawCentredString(self.center_line, self.vert_pos, text)
        self.vert_pos -= padding * 2 + space_below

    def text_block(self, text, font_name, color, font_height=DEFAULT_FONT_HEIGHT):
        if type(text) is str:
            text = text.split("\n")
        assert type(text) is list
        self.c.setFont(font_name, font_height)
        self.c.setFillColor(color)
        for line in text:
            self.vert_pos -= font_height
            self.c.drawString(self.left_margin, self.vert_pos, line)
        self.vert_pos -= DEFAULT_MIN_VERTICAL_SPACING

    def left_right_text(self, left_text: str, right_text: str, font_name, color=DEFAULT_COLOR, font_height=DEFAULT_FONT_HEIGHT):
        self.c.setFont(font_name, font_height)
        self.c.setFillColor(color)
        self.vert_pos -= font_height
        self.c.drawString(self.left_margin, self.vert_pos, left_text)
        self.c.drawRightString(self.right_edge - self.right_margin, self.vert_pos, right_text)
        self.vert_pos -= DEFAULT_MIN_VERTICAL_SPACING

    def centered_img(self, fully_qualified_image_file: str, width=100, height=100, border=True):
        self.vert_pos -= height
        x = self.center_line - width / 2
        self.place_img(fully_qualified_image_file, x, self.vert_pos, width, height, border=border)
        self.vert_pos -= DEFAULT_MIN_VERTICAL_SPACING

    def place_img(self, fully_qualified_image_file: str, x, y, width=100, height=100, border=True, transparent=False):
        img = ImageReader(fully_qualified_image_file)
        mask = None
        if transparent:
            mask = "auto"
        self.c.drawImage(img, x, y, width, height, anchor='sw', anchorAtXY=True, showBoundary=border, mask=mask)

    def vertical_space(self, height):
        self.vert_pos -= height