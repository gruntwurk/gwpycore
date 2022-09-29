import logging

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER

styles = getSampleStyleSheet()

LOG = logging.getLogger("main")

__all__ = [
    "SheetLabelsDoc",
]


class SheetLabelsDoc(BaseDocTemplate):
    """
    A ReportLab document template for printing sheets of labels.
    Given the size of each individual label, the grid size and subsequent
    margins are automatically determined.
    """

    AVERY_5160_WIDTH = 189  # 2 5/8"
    AVERY_5160_HEIGHT = 72  # 1"

    def __init__(self, filename, label_width=AVERY_5160_WIDTH, label_height=AVERY_5160_HEIGHT, pagesize=LETTER, horizontal_padding=3, **kw):
        super().__init__(filename, pagesize=pagesize, pageTemplates=[], showBoundary=0, **kw)
        self.horizontal_padding = horizontal_padding
        self.label_height = label_height
        self.label_width = label_width
        self.calculate_label_grid()
        frames = self.create_col_frames()
        self.addPageTemplates(PageTemplate(id="label_sheet", frames=frames))

    def calculate_label_grid(self):
        """
        Given the size of each individual label, the grid size and subsequent
        margins are automatically determined.
        """
        page_width, page_height = self.pagesize
        self.rows = int(page_height / self.label_height)
        self.cols = int(page_width / self.label_width)
        self.leftMargin = self.rightMargin = (page_width - (self.label_width * self.cols)) / 2.0
        self.topMargin = self.bottomMargin = (page_height - (self.label_height * self.rows)) / 2.0

    def create_col_frames(self):
        """
        Creates a frame for each column of labels.

        :return: A list of frames.
        """
        frames = []
        for col_number in range(self.cols):
            offset = col_number * self.label_width
            f = Frame(id=f'col{str(col_number)}',
                      x1=self.leftMargin + offset,
                      y1=self.bottomMargin,
                      width=self.label_width, height=self.label_height * self.rows,
                      leftPadding=self.horizontal_padding, rightPadding=self.horizontal_padding,
                      topPadding=0, bottomPadding=0,
                      showBoundary=0)
            frames.append(f)
        return frames
