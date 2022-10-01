"""
Supplementary General-Purpose Flowables:

* LeftRightText -- Because Paragraph doesn't understand tab stops.

"""
from gwpycore import NamedColor

from reportlab.platypus import Flowable, UseUpSpace

__all__ = [
    "LeftRightText",
    "VerticalTab",
]


DEFAULT_FONT = "Roboto Bold"
DEFAULT_COLOR = NamedColor.BLACK.float_tuple()
DEFAULT_FONT_HEIGHT = 10  # pt


class LeftRightText(Flowable):
    """
    A ReportLab Flowable that produces one line of text in two parts: a left
    part and a right part. The left part is left-alligned, while the right
    part is right-alined.

    :param left_text: The str to be printed on the left
    :param right_text: The str to be printed on the right
    :param font_name: default is Roboto Bold
    :param color: A 4-tuple of float. Defalut is black.
    :param font_height: Default is 10.
    :param leading: Default is the font_height + 4.
    """
    def __init__(self, left_text: str, right_text: str,
                 font_name=DEFAULT_FONT, color=DEFAULT_COLOR,
                 font_height=DEFAULT_FONT_HEIGHT, leading=None):
        self.avail_width = 0
        self.left_text = left_text
        self.right_text = right_text
        self.font_name = font_name
        self.color = color
        self.font_height = font_height
        self.leading = leading if leading else font_height + 4
        super().__init__()

    def wrap(self, availWidth, availHeight):
        # Remember the available width so we know where to draw the right part.
        self.avail_width = availWidth
        return (self.avail_width, self.leading)

    def draw(self):
        assert self.avail_width > 0
        self.canv.setFont(self.font_name, self.font_height)
        self.canv.setFillColor(self.color)
        self.canv.drawString(0, 0, self.left_text)
        self.canv.drawRightString(self.avail_width, 0, self.right_text)


class VerticalTab(UseUpSpace):
    def __init__(self, height_required_at_bottom):
        self.height_required_at_bottom = height_required_at_bottom

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    def wrap(self, availWidth, availHeight):
        return (availWidth, availHeight - self.height_required_at_bottom - 1e-8)
