import sys
import time

from PyQt5.QtWidgets import QApplication

from gwpycore.gw_gui import SimpleControlPanel
from gwpycore.gw_strings import phonetic_spelling

sys.coinit_flags = 2
import pywinauto


class NotepadControlPanel(SimpleControlPanel):
    def __init__(self):
        SimpleControlPanel.__init__(self, title="Notepad Automation", grid_height=9, cell_width=200)

        self.main_label = self.add_label("-- Main Functions --")
        self.chk_all_caps = self.add_checkbox("Use ALL CAPS", tip="Make the text SHOUT.")
        self.btn_write_letter = self.add_action_button("Write a Letter", callback=write_letter)
        self.btn_my_signature = self.add_action_button("Add a Signature", callback=my_signature, tip="Name and City")
        self.btn_font_1 = self.add_action_button("Change the Font to Courier New", callback=select_courier_font)
        self.btn_font_2 = self.add_action_button("Change the Font to Cambria", callback=select_cambria)
        self.btn_print_action = self.add_action_button("Print the Document", callback=print_action)
        self.btn_exit = self.add_action_button("Exit Wihtout Saving", callback=exit_without_saving)

        self.move_to_next_cell()  # add a spacer (skip a cell)
        self.meta_label = self.add_label("-- Meta Functions --")
        self.btn_identify_window = self.add_action_button("Identify Window", callback=identify_window, tip="Draw a box around the Noetpad window.")
        self.btn_discover_controls = self.add_action_button("Discover Controls", callback=discover_controls, tip="Print a tree of all of Notepad's child controls.")


def main():
    """
    This example is a control panel with several pushbuttons that automate Windows Notepad (using pywinauto).
    """
    qt_app = QApplication(sys.argv)
    global cp, auto_app, np
    cp = NotepadControlPanel()
    auto_app = pywinauto.application.Application()
    try:
        auto_app.start("Notepad.exe")
        np = auto_app.UntitledNotepad
    except Exception as e:
        print(e)
        sys.exit(1)
    cp.show()
    sys.exit(qt_app.exec_())


def write_letter():
    body = "To Whom It May Concern,\n\nThis letter was auto-generated.\n"
    if cp.chk_all_caps.isChecked():
        body = body.upper()
    np.Edit.set_edit_text(body)


def my_signature():
    textbox = np.Edit
    sig = "\nSincerely,\nJohn Smith -- Las Vegas, Nevada"
    if cp.chk_all_caps.isChecked():
        sig = sig.upper()
    textbox.set_edit_text(textbox.text_block() + sig)


def select_cambria():
    np.menu_select("Format -> Font")
    dlg = auto_app.top_window()
    dlg.type_keys("Cambria")
    dlg.OK.click()


def select_courier_font():
    np.menu_select("Format -> Font")
    dlg = auto_app.top_window()
    dlg.type_keys("Courier{SPACE}New")
    dlg.OK.click()


def print_action():
    np.menu_select("File -> Print")
    # time.sleep(0.2)
    # dlg = auto_app.top_window()
    auto_app.PrintDialog.PrintButton.click()


def exit_without_saving():
    np.menu_select("File -> Exit")  # or np.type_keys("%fx")
    # time.sleep(0.2)
    dlg = auto_app.NotepadDialog
    if dlg.exists():
        dlg.DontSaveButton.click()
    sys.exit(0)


def identify_window():
    np.draw_outline()


def discover_controls():
    dlg = auto_app.top_window()
    dlg.print_control_identifiers()


if __name__ == "__main__":
    main()
