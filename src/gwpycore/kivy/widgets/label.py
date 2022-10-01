import logging

from kivy.uix.label import Label
from kivy.properties import NumericProperty
from gwpycore.kivy.widgets.background import BackgroundColor

LOG = logging.getLogger("gwpy")


__all__ = [
    "GWLabel",
]


class GWLabel(Label, BackgroundColor):
    """
    A variation of the kivy Label widget that defaults to using the whole space
    alloted to the label (rather than always centering the text).
    It also inherits from BackgroundColor. Thus, all of these properties can be combined:

    * text_padding (new) defaults to 8.
    * background_color (from BackgroundColor) is required.
    * halign now defaults to 'left'.
    * valign now defaults to 'top'.

    Foe example, if the label is 200px x 100px, and the text_padding is 8, then
    the text rectangle will be 184 x 84 (centered), and the text will placed in
    the upper left of that.
    """

    text_padding = NumericProperty(8)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'top'

        # if self.background_padding < 4:
        #     self.background_padding = 4

    def on_texture_size(self, *args):
        # LOG.trace("Reacting to texture size change")
        text_actual_height = self.texture_size[1]
        new_height = text_actual_height + (2 * self.text_padding)
        # This if-statament gaurds against an infinate loop (changing the height calls on_size)
        # LOG.debug("new_height = {}".format(new_height))
        # LOG.debug("self.height = {}".format(self.height))
        if new_height != self.height:
            # LOG.debug("setting new height")
            self.height = new_height

    def on_pos(self, *args):
        # LOG.trace("Reacting to pos change")
        self._determine_new_size()

    def on_size(self, *args):
        # LOG.trace("Reacting to size change")
        self._determine_new_size()

    def _determine_new_size(self):
        text_width_available = self.size[0] - (2 * self.text_padding)
        # LOG.debug("current text_width = {}".format(self.text_size[0]))
        # LOG.debug("text_width_available = {}".format(text_width_available))
        if self.text_size[0] != text_width_available:
            # LOG.trace("Recalculating text dimensions.")
            self.text_size = (text_width_available, None)
            self.texture_update()
        else:
            BackgroundColor.on_size(self)
