import logging

from kivy.uix.button import Button
from gwpycore.core.gw_colors import NamedColor
from gwpycore.kivy.widgets.background import BackgroundColor

LOG = logging.getLogger("gwpy")


__all__ = [
    "GWButton",
]


class GWButton(Button, BackgroundColor):
    """
    A variation of the kivy Button widget that also inherits from BackgroundColor.
    It defaluts to having no background image so that the background color
    is not muddled. The default background color is 20% gray.
    """

    def __init__(self, **kwargs):
        self.background_normal = ''
        self.background_color = NamedColor.GRAY80.float_tuple()
        super().__init__(**kwargs)

