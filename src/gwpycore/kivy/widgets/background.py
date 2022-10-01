import logging
from kivy.uix.widget import Widget
from kivy.graphics import Canvas, Color, Rectangle
from kivy.properties import ColorProperty

LOG = logging.getLogger("gwpy")


__ALL__ = [
    'BackgroundColor',
]


class BackgroundColor(Widget):
    """
    A composable widget for setting the background color of another widget.

    Example (in the `.kv` file)
    ~~~~
    <MyLabel@Label+BackgroundColor>
        background_color: 0, 1, 0, 0.25
    ~~~~

    See also GWLabel.
    """
    background_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pos(self, *args):
        self._determine_background_size()

    def on_size(self, *args):
        self._determine_background_size()

    def _determine_background_size(self):
        c: Canvas = self.canvas
        c.before.clear()
        with c.before:
            Color(rgba=self.background_color)
            Rectangle(pos=self.pos, size=self.size)


