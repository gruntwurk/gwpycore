from enum import Enum
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty, StringProperty
from gwpycore import class_from_name
DROPDOWN_SELECTION_HEIGHT = 40


class EnumDropDown(Spinner):
    """
    A dropdown widget (aka. spinner) that auto-populates with all of the
    possible values of a given Enum class.

    :example: (in the `.kv` file)
        EnumDropDown:
            enum_class_name: "models.member.MemberRank"
            height_per: 33
            id: _rank
            on_text: root.validate_member_rank()

    The first value in the list (as declared in the enum) is the initial
    selection in the list.

    :property enum_class_name: The class name of the enum that provides the possible values.
    :property height_per: How high (px) to make each choice. Default is 40.
    """
    enum_class_name = StringProperty("")
    height_per = NumericProperty(DROPDOWN_SELECTION_HEIGHT)

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        enum_class: Enum = class_from_name(self.enum_class_name)
        self.values = [e.value for e in enum_class]
        if self.values:
            self.text = self.values[0]
        super().on_kv_post(base_widget)


__ALL__ = [
    'EnumDropDown'
]
