import logging

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.pagesizes import LETTER

LOG = logging.getLogger("main")

__all__ = [
    "create_col_frames",
    "MultiColumnDoc",
    "SheetLabelsDoc",
]


def create_col_frames(doc_template: BaseDocTemplate, page_template_id="page"):
    """
    For the given doc template, this establishes a page template containing a
    frame for each column.
    """
    frames = []
    for col_number in range(doc_template.cols):
        offset = col_number * (doc_template.column_width + doc_template.gutter_width)
        f = Frame(id=f'col{str(col_number)}',
                  x1=doc_template.leftMargin + offset,
                  y1=doc_template.bottomMargin,
                  width=doc_template.column_width, height=doc_template.column_height,
                  leftPadding=doc_template.horizontal_padding, rightPadding=doc_template.horizontal_padding,
                  topPadding=0, bottomPadding=0,
                  showBoundary=doc_template.outline_frames)
        frames.append(f)
    doc_template.addPageTemplates(PageTemplate(id=page_template_id, frames=frames))


class MultiColumnDoc(BaseDocTemplate):
    """
    A ReportLab document template with multiple columns (frames) of equal size.
    """
    DEFAULT_GUTTER = 18  # 1/4"

    def __init__(self, filename, pagesize=LETTER,
                 cols=2,
                 gutter_width=DEFAULT_GUTTER,
                 outline_frames=0, **kw):
        super().__init__(filename, pagesize=pagesize, pageTemplates=[], showBoundary=0, **kw)
        self.horizontal_padding = 0
        self.cols = cols
        self.gutter_width = gutter_width
        self.outline_frames = outline_frames
        create_col_frames(self, page_template_id="multi_column")

    def calculate_frame_info(self):
        """
        The column width and height are automatically determined.
        """
        page_width, page_height = self.pagesize
        self.body_width = page_width - self.leftMargin - self.rightMargin
        self.column_width = (self.body_width - (self.gutter_width * (self.cols -1)))/self.cols
        self.column_height = page_height - self.topMargin - self.bottomMargin


class SheetLabelsDoc(BaseDocTemplate):
    """
    A ReportLab document template for printing sheets of labels.
    Given the size of each individual label, the grid size and subsequent
    margins are automatically determined.
    """
    DEFAULT_GUTTER = 0
    AVERY_5160_WIDTH = 189  # 2 5/8"
    AVERY_5160_HEIGHT = 72  # 1"

    def __init__(self, filename, pagesize=LETTER,
                 label_width=AVERY_5160_WIDTH, label_height=AVERY_5160_HEIGHT,
                 horizontal_padding=0,
                 outline_frames=0, **kw):
        super().__init__(filename, pagesize=pagesize, pageTemplates=[], showBoundary=0, **kw)
        self.horizontal_padding = horizontal_padding
        self.label_height = label_height
        self.column_width = label_width
        self.gutter_width = 0
        self.outline_frames = outline_frames
        self.calculate_frame_info()
        create_col_frames(self, page_template_id="label_sheet")

    def calculate_frame_info(self):
        """
        Given the size of each individual label, the grid size and subsequent
        margins are automatically determined.
        """
        page_width, page_height = self.pagesize
        self.rows = int(page_height / self.label_height)
        self.cols = int(page_width / self.column_width)
        self.leftMargin = self.rightMargin = (page_width - (self.column_width * self.cols)) / 2.0
        self.topMargin = self.bottomMargin = (page_height - (self.label_height * self.rows)) / 2.0
        self.column_height = self.label_height * self.rows

