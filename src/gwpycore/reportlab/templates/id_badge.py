import logging

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

styles = getSampleStyleSheet()

LOG = logging.getLogger("main")

__all__ = [
    "IDBadgeDoc",
]

CR80 = (2.13 * inch, 3.38 * inch)  # ID card page size


class IDBadgeDoc(BaseDocTemplate):
    """
    A ReportLab document template for printing an ID badge.
    """

    def __init__(self, filename, pagesize=CR80, **kw):
        super().__init__(filename, pagesize=pagesize, **kw)
        f = Frame(id='only_col',
                  x1=0,
                  y1=0,
                  width=self.pagesize[0], height=self.pagesize[1],
                  leftPadding=2, rightPadding=2,
                  topPadding=0, bottomPadding=0,
                  showBoundary=0)
        self.addPageTemplates(PageTemplate(id="id_card", frames=[f]))


