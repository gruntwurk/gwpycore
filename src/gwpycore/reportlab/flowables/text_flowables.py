"""
Supplementary General-Purpose Flowables.
"""
from reportlab.platypus import Flowable, UseUpSpace

__all__ = [
    "LeftRightText",
    "VerticalTab",
]


DEFAULT_FONT = "Arial Bold"
DEFAULT_COLOR =  (0, 0, 0)  # black
DEFAULT_FONT_HEIGHT = 10  # pt


class LeftRightText(Flowable):
    """
    A ReportLab Flowable that produces one line of text in two parts: a left
    part and a right part. The left part is left-alligned, while the right
    part is right-alined.

    This is here because the Paragraph flowable doesn't inately understand
    tab stops.

    :param left_text: The str to be printed on the left
    :param right_text: The str to be printed on the right
    :param font_name: default is Arial Bold
    :param color: A 4-tuple of float. Default is black.
    :param font_height: Default is 10.
    :param leading: Default is the font_height + 4.
    """
    def __init__(self, left_text: str, right_text: str,
                 font_name=DEFAULT_FONT, color=DEFAULT_COLOR,
                 font_height=DEFAULT_FONT_HEIGHT, leading=None, horizontal_padding=0):
        self.avail_width = 0
        self.left_text = left_text
        self.right_text = right_text
        self.font_name = font_name
        self.color = color
        self.font_height = font_height
        self.leading = leading or font_height + 4
        self.horizontal_padding = horizontal_padding
        super().__init__()

    def wrap(self, availWidth, availHeight):
        # Remember the available width so we know where to draw the right part.
        self.avail_width = availWidth
        return (self.avail_width, self.leading)

    def draw(self):
        assert self.avail_width > 0
        self.canv.setFont(self.font_name, self.font_height)
        self.canv.setFillColor(self.color)
        self.canv.drawString(self.horizontal_padding, 0, self.left_text)
        self.canv.drawRightString(self.avail_width - self.horizontal_padding, 0, self.right_text)


class VerticalTab(UseUpSpace):
    """
    A ReportLab Flowable that skips down to where the remaining text for the
    column (as specified by the combined height of that pending text) will
    exactly fit at the bottom of the column.

    :param height_required_at_bottom: The amount of vertical space needed for
    the pending text
    """
    def __init__(self, height_required_at_bottom):
        self.height_required_at_bottom = height_required_at_bottom

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def wrap(self, availWidth, availHeight):
        return (availWidth, availHeight - self.height_required_at_bottom - 1e-8)

