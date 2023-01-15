import logging
from typing import Tuple
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.core.window import Window

# from ...core.keystrokes import parse_keystroke_expression


LOG = logging.getLogger("gwpy")


__ALL__ = [
    'HotKey',
    'MultiKeystrokeListener',
]

TAB = 9
ENTER = 13


# ############################################################################
#                                                                       HotKey
# ############################################################################

class HotKey(Widget):
    """
    A composable widget for binding a key to an action of another widget.

    :param hot_key: A keystroke expression that will set the focus to this
    widget and/or invoke this widget's action.
    :param listener_widget: Which parent/ancestor widget is to handle the hot_key.
    Defaults to the app's main window.
    :param next_widget: The widget to obtain focus when tabbing off of this widget (`tab`).
    :param prev_widget: The widget to obtain focus when back-tabbing off of this widget (`shift+tab`).
    :param enter_means_tab: Whether or not the `enter` key will also tab off.

    Example (in the `.kv` file)
    ~~~~
    <MyButton@Button+HotKey>
        hot_key: 'shift+alt+f15'
        next_widget: _some_id
        prev_widget: _some_other_id
        enter_means_tab: True

    ~~~~

    See also GWLabel.
    """
    _hot_key = StringProperty()
    _next_widget = ObjectProperty()
    _prev_widget = ObjectProperty()
    _enter_means_tab = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def next_widget(self):
        """Tab-order forward (Tab key, and maybe Enter key)."""
        return self._next_widget

    @next_widget.setter
    def next_widget(self, value):
        self._next_widget = self.widget_by_id(value)

    @property
    def prev_widget(self):
        """Tab-order reversed (Shift-Tab)."""
        return self._prev_widget

    @prev_widget.setter
    def prev_widget(self, value):
        self._prev_widget = self.widget_by_id(value)

    @property
    def enter_means_tab(self):
        """The enter_means_tab property."""
        return self._enter_means_tab

    @enter_means_tab.setter
    def enter_means_tab(self, value):
        self._enter_means_tab = value

    @property
    def hot_key(self):
        """The hot_key property."""
        return self._hot_key

    @hot_key.setter
    def hot_key(self, value: Tuple):
        self._hot_key = value
        self._keycode = value[0]
        self._modifiers = value[1:]

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        LOG.debug(f"keycode = {keycode}")
        LOG.debug(f"modifiers = {modifiers}")
        # key, key_str = keycode
        # if key == ENTER and self.enter_means_tab:
        #     key = TAB
        # key_expr = [key_str]
        # key_expr.extend(modifiers)
        # specific_keystroke = parse_keystroke_expression(key_expr)
        # if key_str == 'tab' or (key_str == 'enter' and self.enter_means_tab):
        #     fwd = True
        #     if ('shift' in modifiers or 'rshift' in modifiers):
        #         fwd = False
        #     if fwd and self._next_widget:
        #         self._next_widget.focus = True
        #         # self._next_widget.select_all()
        #     elif self._prev_widget:
        #         self._prev_widget.focus = True
        #         # self._prev_widget.select_all()
        # else:
        super()._keyboard_on_key_down(window, keycode, text, modifiers)


class MultiKeystrokeListener(Widget):
    """
    An invisble widget that listens to the keyboard for complete multi-keystroke
    combinations, e.g. ctrl+shift+f1. All other noisy events are ignored.
    For example, on the way to the ctrl+shift+f1 combination, we get three
    key_down and three key_up events, but only the last key_down event is
    significant. Here, we call that a "key press".

    :param on_key_press: A callable to handle the resultant key press (the one significant key_down)
    """
    do_key_press: ObjectProperty()

    def __init__(self, **kwargs):
        super(MultiKeystrokeListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        # if self._keyboard.widget:
        #     # If it exists, this widget is a VKeyboard object which you can use
        #     # to change the keyboard layout.
        #     pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        pass
        # self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        # self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # This handler is called spuriously. For example, on the way to a
        # ctrl+alt+f1, it gets called for each of the keydowns:
        #     ctrl, ctrl+shift, ctrl+shift+f1.
        # Also, if there is a pause in between, then the keyboard may auto
        # repeat, as in:
        #     ctrl, ctrl, ctrl, ctrl, ctrl, ctrl, ctrl+shift, ctrl+shift+f1
        # So, we just want to remember the last call, then only act on it
        # once we start to receive key_up calls.
        self.latest_down = (keycode, modifiers)
        # print('--- DOWN ---')
        # print('keycode[0]:', keycode[0])
        # print('keycode[1]:', keycode[1])
        # print('text:', text)
        # print('modifiers:', modifiers)

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        # Now we can act on the last keydown we saw.
        if self.latest_down:
            keycode, modifiers = self.latest_down
            self.do_key_press(keycode, modifiers)
            # Be sure to only act once, e.g. in the case of ctrl+shift+f1,
            # we'll get 3 calls to key_up (in random order)
            self.latest_down = None

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True




