from kivy.uix.scrollview import ScrollView

__all__ = [
    "GWScrollView",
]


class GWScrollView(ScrollView):
    """
    A ScrollView that defaults to vertical scrolling using a scroll bar (or the wheel).

    TIP: Make sure the contents of the scrollview have `size_hint_y: None`;
    otherwise Kivy will compress the contents to fill the view, defeating the
    point of scrolling.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # A common mistake is to forget to set the scroll_type
        self.scroll_type = ['bars']
        self.do_scroll_x = False
        self.bar_width = 6