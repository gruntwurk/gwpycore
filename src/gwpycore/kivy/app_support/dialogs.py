"""
Frequently Used Message Dialog Boxes

* inform_user()
* ask_user_yes_no()
* ask_user_to_choose()
* choose_file()
* choose_folder()
"""

from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Callable, List, Tuple, Union

from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from gwpycore import Singleton, GWError

LOG = logging.getLogger("gwpy")


def optimal_dialog_size(prefered_width=300, prefered_height=200) -> Tuple[int, int, int, int]:
    width = min(prefered_width, Window.width)
    height = min(prefered_height, Window.height)
    pos_x = max((Window.width - width) * 0.5, 0)
    pos_y = max((Window.height - height) * 0.5, 0)
    return (width, height, pos_x, pos_y)


class GWDialog(ABC):
    """
    Base class for the dialog boxes that follow.
    """
    _popup: Popup = None
    _payload = None  # the main widget for the dialog (a message Label, a FileChooserListView, etc.)
    _user_callback_ok = None
    _user_callback_cancel = None
    _title = "Question"

    def __init__(self, prefered_width=300, prefered_height=200, *args, **kwargs):
        super().__init__(*args, **kwargs)

        CONTROLS_HEIGHT = 30
        w, h, x, y = optimal_dialog_size(prefered_width, prefered_height)

        # self._inner_box = RelativeLayout(size_hint_y=None, height=h - CONTROLS_HEIGHT, pos_hint={"top": 1})
        self._inner_box = RelativeLayout(size_hint_y=1.0, pos_hint={"top": 1})
        self._controls_box = BoxLayout(size_hint_y=None, height=CONTROLS_HEIGHT, orientation="horizontal", pos_hint={"y": 0})
        self._outer_box = BoxLayout(orientation="vertical")
        self._outer_box.add_widget(self._inner_box)
        self._outer_box.add_widget(self._controls_box)
        self._popup = Popup(title=" ", content=self._outer_box, size_hint_x=None, size_hint_y=None)
        self._popup.width = w
        self._popup.height = h
        self._popup.pos = (x, y)

    @property
    def buttons(self):
        return self._buttons
    @buttons.setter
    def buttons(self, value):
        self._buttons = value
        self._controls_box.clear_widgets()
        self._controls_box.pos = self._controls_box.parent.pos
        for button_name in self._buttons:
            btn = Button(text=self._buttons[button_name])
            if button_name == "ok":
                btn.on_release = self.on_ok
            elif button_name == "cancel":
                btn.on_release = self.on_cancel
            self._controls_box.add_widget(btn)

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = value

    def set_user_callbacks(self, user_on_ok: Callable = None, user_on_cancel: Callable = None):
        self._user_callback_ok = user_on_ok
        self._user_callback_cancel = user_on_cancel

    def add_widget(self, widget, *args, **kwargs):
        # widget.height = self._inner_box.height
        # widget.width = self._inner_box.width
        widget.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        return self._inner_box.add_widget(widget, *args, **kwargs)

    def open(self):
        self._popup.title = self._title
        self._popup.open()

    @abstractmethod
    def on_ok(self, *args):
        pass

    @abstractmethod
    def on_cancel(self, *args):
        pass


# ############################################################################
#                                                           INFORM_USER DIALOG
# ############################################################################

@Singleton
class InformDialog(GWDialog):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # self._msg = Label(size_hint_y=None, height=30, pos_hint={"center_x": 0.5, "center_y": 0.5}, valign='center', halign='center')
        self._payload = Label(pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self._payload)

    def inform(self, msg):
        self._payload.text = str(msg)
        self.open()

    def on_ok(self):
        self._popup.dismiss()
        if self._user_callback_ok:
            self._user_callback_ok(self._result)

    def on_cancel(self, *args):
        self._popup.dismiss()
        if self._user_callback_cancel:
            self._user_callback_cancel()
        elif self._user_callback_ok:
            self._user_callback_ok(None)



def inform_user(msg, on_ok: Callable = None, on_cancel: Callable = None, ok="OK", title="Information"):
    """
    Pops up a modal dialog to inform the user of something.
    :param msg: The text of the information.
    :param ok: The wording on the OK button (default: "OK")
    :param title: The title of the dialog box (default: "Information")
    """
    dlg = InformDialog()
    dlg.set_user_callbacks(on_ok, on_cancel)
    dlg.buttons = {"ok": ok}
    dlg.title=title
    dlg.inform(msg)


# ############################################################################
#                                                       ASK_USER_YES_NO DIALOG
# ############################################################################

@Singleton
class YesNoDialog(GWDialog):
    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)
        self._payload = Label(valign='center', halign='center')
        self.add_widget(self._payload)

    def ask(self, msg):
        self._payload.text = msg
        self.open()

    def on_ok(self):
        self._popup.dismiss()
        if self._user_callback_ok:
            self._user_callback_ok(self._result)

    def on_cancel(self, *args):
        self._popup.dismiss()
        if self._user_callback_cancel:
            self._user_callback_cancel()
        elif self._user_callback_ok:
            self._user_callback_ok(None)



def ask_user_yes_no(msg, on_yes: Callable, on_no: Callable = None, yes="YES", no="NO", title="Question") -> None:
    """
    IMPORTANT:
        This function exits BEFORE the question is answered. A callback method
        is needed to act on the answer.

    :param msg: The text of the question to ask.
    :param on_yes: A function/method that is called if the user answers "yes".
    :param on_no: A function/method that is called if the user answers "no" --
        Alternatively, if on_no is None (default), then the on_yes function will
        be called instead but will passed a value of None. In that case, make
        sure the function is declared to accept a single argument with a
        default value of True.
    :param title: The title of the dialog box (default: "Question:")
    :param yes: The wording on the Yes button (default: "Yes")
    :param no: The wording on the No button (default: "No")
    :return: None!!! (see note above).
    """
    dlg = YesNoDialog()
    dlg.set_user_callbacks(on_yes, on_no)
    dlg.buttons = {"ok": yes, "cancel": no}
    dlg.title = title
    # dlg = YesNoDialog(on_ok=on_yes, on_cancel=on_no, ok_button=yes, cancel_button=no, title=title)
    dlg.ask(msg)


# ############################################################################
#                                                               CHOICES DIALOG
# ############################################################################

def ask_user_to_choose(msg: str, callback, choices: List[str], title="Please Make a Selection") -> None:
    """
    Pops up a dialog that requests the user to select from a list of choices
    in a drop-down box.

    IMPORTANT:
        This function exits BEFORE the question is answered. A callback method
        is needed to act on the answer.

    :param msg: The text of the question to ask.
    :param callback: A function/method that accepts the selected list item.
    :param choices: a list of strings
    :param title: The title of the dialog box (default: "Please Make a Selection")
    :param icon: (not yet; default None)
    :param autoclose: Whether or not clicking outside th dialog will close the
    dialog, without calling the callback function at all (default: False)
    :return: None!!! (see note above).
    """
    pass


    # def startProgressBox(self, title: str, msg: str, cancelButton: str, empty: int, full: int) -> QProgressDialog:
    #     box = QProgressDialog(msg, cancelButton, empty, full)
    #     box.setWindowModality(Qt.WindowModal)
    #     box.setWindowTitle(title)
    #     box.show()
    #     return box


# ############################################################################
#                                                                 FILE CHOOSER
# ############################################################################

# @Singleton
class FileChooser(GWDialog):
    _input: TextInput
    def __init__(self, **kwargs) -> None:
        self._use_icon_view = False
        self._allow_freeform = False
        super().__init__(prefered_width=800, prefered_height=600, **kwargs)

    def set_options(self, use_icon_view=False, allow_freeform=False):
        self._use_icon_view = use_icon_view
        if allow_freeform:
            raise GWError("FileChooser's allow_freeform option is not yet available.")
            # self._allow_freeform = allow_freeform

    def open(self, starting_path: str):
        self._payload = FileChooserIconView() if self._use_icon_view else FileChooserListView()
        self._payload.pos_hint={"top": 1.0}
        if self.dir_select:
            self._payload.dirselect = self.dir_select
            self._payload.filters.append('~~~~~~~')  # match nothing (just folders)
        self.add_widget(self._payload)
        self._payload.path = starting_path
        # if self._allow_freeform:
        #     self._input = TextInput(size_hint_y=None, height=30, multiline=False, pos_hint={"y": 0})
        #     self.add_widget(self._input)
        #     self._input.text = ""
        super().open()

    def on_ok(self):
        self._popup.dismiss()
        if self._user_callback_ok:
            self._user_callback_ok(self._payload.path, self._payload.selection)

    def on_cancel(self, *args):
        self._popup.dismiss()
        if self._user_callback_cancel:
            self._user_callback_cancel()


def choose_file(starting_path: Union[Path,str],
                on_ok: Callable, on_cancel: Callable = lambda x: x,
                use_icon_view=False, allow_freeform=False,
                title="Select File", dir_select=False) -> None:
    """
    :param starting_path: Root of the directory tree within which the file or dir is to be selected.
    :param callback: A function that accepts one argument -- the selected path (or None if user cancels out).

    IMPORTANT:
        This function exits BEFORE the selection is made. A callback method
        is needed to act on the (non)selection.

    :return: None!!! (see note above).
    """
    dlg = FileChooser()
    dlg.dir_select = dir_select
    dlg.set_user_callbacks(on_ok, on_cancel)
    dlg.set_options(use_icon_view, allow_freeform)
    dlg.buttons = {"ok": "Select", "cancel": "Cancel"}
    dlg.title = title
    dlg.open(str(starting_path))


def choose_folder(starting_path: Union[Path,str],
                  on_ok: Callable, on_cancel: Callable = None,
                  use_icon_view=False, allow_freeform=False,
                  title="Select Folder", dir_select=True) -> None:
    choose_file(starting_path=starting_path,
                on_ok=on_ok, on_cancel=on_cancel,
                use_icon_view=use_icon_view, allow_freeform=allow_freeform,
                title=title, dir_select=True)


__all__ = [
    "inform_user",
    "ask_user_yes_no",
    "ask_user_to_choose",
    "choose_file",
    "choose_folder",
    # "ICON_ERROR", "ICON_WARN", "ICON_WARNING", "ICON_INFO", "ICON_QUESTION",
]
