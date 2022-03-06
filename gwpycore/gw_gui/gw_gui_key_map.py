import csv
from io import FileIO
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from gwpycore.gw_gui.gw_gui_theme import GWAssets, ThemeMetaData, ThemeStructure
import logging
from typing import Any, Optional, Tuple, Union
from pathlib import Path

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction

# TODO Move all PyQT support to a seperate module (gwpyqt)

LOG = logging.getLogger("main")


class KeyMapAssets(GWAssets):
    """
    Handles reassigning keyboard shortcuts and related options, according to
    pre-determined and/or custom layouts.

    This relies on the application using QAction objects, each with a name that
    begins with "action_". The rest of the name is considered the action's "identifier".

    A keymap asset consists of a CSV file (**/*.csv). The name of the file is the
    name of the theme.
    (Note: "default" is a reserved theme name. Note also that if the same file
    name appears in two different subfolders, only one will be used -- at random.)

    Each CSV file is assumed to have one header row, which is ignored.
    Each data row then has at least 3 columns:

    Column 1 is the action identifier (e.g. "help" for action_help)
    Column 2 replaces the text description of the action (e.g. "Website &Documentation")
    Column 3 is the primary key sequence (e.g. "Ctrl+F1")
    Columns 4-6 are optional alternative key sequences.
    Column 7 replaces the tool tip of the action (e.g. "Opens the default broswer with the online documentation")

    If columns 4-6 are not supplied, any existing alternative key sequences are removed.
    Likewise, if column 7 is not supplied, the tip is changed to "".

    Parameters:

    * asset path -- the folder path to the keymap files (*.csv files, in optional subfolders).
    * parent -- The instance of the dialog/window class that holds the QAction objects.
    * advanced_keymap -- the default keymap consists of however all of the actions are defined within the .UI file
      plus whatever is passed in as the advanced_keymap. For example, QTDesigner only allows you to define one
      keystroke shortcut per action. So, any actions that need to have alternative keystroke shortcuts defined
      can be done so via an advanced_keymap.

    """
    def __init__(self, asset_path: Union[Path, str], parent: Optional[QObject], advanced_keymap, **kwds) -> None:
        super().__init__(asset_path, **kwds)
        self.parent = parent
        self.advanced_keymap = advanced_keymap
        self.theme_structure = ThemeStructure.KEYMAP  # Tells findThemes to look for **/*.csv files
        self.keymap_meta: ThemeMetaData = None
        self.keymap_list = [x for x in self.themes().keys()]
        self.keymap_list.insert(0, "default")
        self.current_keymap = 0
        self.load_keymap_data(self.advanced_keymap)
        self.remember_default_keymap()

    def remember_default_keymap(self):
        self.default_keymap = []
        all_actions = self.parent.findChildren(QAction)
        for action in all_actions:
            self.default_keymap.append(self.get_action_definition(action))

    def apply_theme(self, theme_name):
        """
        (First, call themes() to see what's available.)
        """
        if not self._set_theme(theme_name):
            return    # already set, nothing to do

        if self.theme_name == "default":
            self.load_keymap_data(self.default_keymap)
            return
        self.load_keymap_file(self.theme_metadata.filename)

    def update_action(self, ident: str, text: str, key_seq_1: str, key_seq_2="", key_seq_3="", key_seq_4="", tip=""):
        if action := self.get_action(ident):
            action.setText(text)
            key_sequences = [QKeySequence(key_seq_1)]
            if key_seq_2:
                key_sequences.append(QKeySequence(key_seq_2))
            if key_seq_3:
                key_sequences.append(QKeySequence(key_seq_3))
            if key_seq_4:
                key_sequences.append(QKeySequence(key_seq_4))
            action.setShortcuts(key_sequences)
            action.setToolTip(tip)

    def get_action(self, ident: str) -> QAction:
        action_name = "action_"+ident
        if hasattr(self.parent,action_name):
            return getattr(self.parent, action_name)
        return None

    def get_action_info(self, ident: str) -> Optional[Tuple[str, str, str]]:
        """
        Returns a tuple with the action's: keystroke shortcut(s) (comma-separated),
        short description (sans &), and the tool tip.
        Use this, for example, when displaying help information.
        """
        a = self.get_action(ident)
        if a:
            shortcuts = a.shortcuts()
            shortcutTexts = []
            for scut in shortcuts:
                if scut:
                    shortcutTexts.append(scut.toString())
            return (", ".join(shortcutTexts), a.text().replace("&", ""), a.toolTip())
        return None

    def get_action_definition(self, action: QAction) -> str:
        """
        Returns a CSV row for the given action.
        """
        values = [action.text()]
        shortcuts = action.shortcuts()
        for scut in shortcuts:
            if scut:
                values.append(scut.toString())
        while len(values) < 5:
            values.append("")
        values.append(action.toolTip())
        return (", ".join(values))

    def load_keymap_file(self, filepath: str):
        """
        throws: GruntWurkConfigError
        """
        # LOG.debug(f"Loading keymap from = {filepath}")
        with open(filepath, newline="") as csvfile:
            self.load_keymap_data(csvfile, init_mode=False)

    def load_keymap_data(self, data):
        """
        data -- a list of strings (or anything else that csv.reader() accepts)
        throws: GruntWurkConfigError
        """
        keymap = csv.reader(data)
        bad_idents = []
        for i, row in enumerate(keymap):
            if i > 0:
                ident = row[0]
                # LOG.debug(f"{i}: ident = {ident}")
                if not self.get_action(ident):
                    bad_idents.append(ident)
        if bad_idents:
            bad_idents_str = ", ".join(bad_idents)
            raise GruntWurkConfigError(f"Invalid key mapping. No such action identifier(s) as {bad_idents_str}.")
        if data is FileIO:
            data.seek(0)

        keymap = csv.reader(data)
        for i, row in enumerate(keymap):
            # check the header row
            if i == 0:
                if row != ["Action Identifier", "Action Label", "Key Seq 1", "Key Seq 2", "Key Seq 3", "Key Seq 4", "Tip"]:
                    raise GruntWurkConfigError('Invalid key map. The header line must be "Action Identifier,Action Label,Key Seq 1,Key Seq 2,Key Seq 3,Key Seq 4,Tip" exactly.')
            else:
                self.update_action(*row)

__all__ = ("KeyMapAssets",)


