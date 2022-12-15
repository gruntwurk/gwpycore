import logging
from enum import Enum
from kivy.uix.spinner import Spinner, SpinnerOption
# from kivy.uix.dropdown import DropDown
from kivy.properties import NumericProperty, StringProperty

from ...core.colors import float_tuple, color_outline
from ...core.typing_utils import class_from_name


LOG = logging.getLogger("gwpy")
DEFAULT_DROPDOWN_SELECTION_HEIGHT = 40


class DropDownChoice(SpinnerOption):
    def __init__(self, text: str, **kwargs):
        super(DropDownChoice, self).__init__(text=text, **kwargs)

    def configure(self, parent, *args):
        self.height = parent.height_per
        colorize_widget_per_enum(self, parent.enum_class)


class EnumDropDown(Spinner):
    """
    A dropdown widget (aka. spinner) that auto-populates with all of the
    possible values of a given Enum class.

    * If the Enum class has a (class) method called `default_enum()`, then
      that method will determine the initial value for the spinner;
      otherwise, the first value in the list (as declared in the enum class)
      will be used.
    * If the Enum class has a (class) method called `by_value()`, then this
      widget will know how to get back to the enum by the text that is
      displayed.
    * In that case, if the Enum class also has a (regular) method called
      `color()`, then that method will be called to set the background
      color of the choice (which is merely a Button). `color()` needs to
      return an RGB 3-tuple or an RGBA 4-tuple of ints (0-255).

    :example: (in the `.kv` file)
        EnumDropDown:
            enum_class_name: "models.member_attributes.MemberRank"
            height_per: 33
            id: _rank
            on_text: root.validate_member_rank()

    :property enum_class_name: The class name of the enum that provides the possible values.

    :property height_per: How high (px) to make each choice. Default is 40.
    """
    enum_class_name = StringProperty("")
    height_per = NumericProperty(DEFAULT_DROPDOWN_SELECTION_HEIGHT)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.option_cls = DropDownChoice

    def on_kv_post(self, base_widget):
        self.enum_class: Enum = class_from_name(self.enum_class_name)
        self.values = [e.value for e in self.enum_class]
        if self.values:
            self.configure_each_choice()
            if hasattr(self.enum_class, 'default_enum'):
                self.text = self.enum_class.default_enum().value
            else:
                self.text = self.values[0]
        super().on_kv_post(base_widget)

    def configure_each_choice(self):
        container = self._dropdown.children[0]
        # LOG.debug("container = {}".format(container))
        for choice in container.children:
            # LOG.debug("choice = {}".format(choice))
            choice.configure(parent=self)

    def on_text(self, *args):
        colorize_widget_per_enum(self, self.enum_class)


def colorize_widget_per_enum(widget, enum_class):
    if hasattr(enum_class, "by_value"):
        enum = enum_class.by_value(widget.text)
        if hasattr(enum, "color"):
            widget.background_normal = ''
            widget.background_color = float_tuple(enum.color())
            widget.color = float_tuple(color_outline(enum.color()))


__ALL__ = [
    'EnumDropDown'
]
