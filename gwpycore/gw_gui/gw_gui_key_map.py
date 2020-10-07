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


LOG = logging.getLogger("main")


class KeyMapAssets(GWAssets):
    """
    Handles reassigning keyboard shortcuts and related options,
    according to pre-determined and/or custom layouts.
    """
    def __init__(self, asset_path: Union[Path, str], parent: Optional[QObject], default_keymap, **kwds) -> None:
        super().__init__(asset_path, **kwds)
        self.parent = parent
        self.default_keymap = default_keymap
        self.theme_structure = ThemeStructure.KEYMAP
        self.keymap_meta: ThemeMetaData = None
        self.conf_name = "keymap.conf"
        self.load_keymap_data(self.default_keymap)

    def apply_theme(self):
        """
        Note: Call themes() and set_theme() before calling apply_theme().
        """
        if self.theme_name == "default":
            self.load_keymap_data(self.default_keymap)
            return
        self.load_keymap_file(self.theme_metadata.filename)

    def update_action(self, ident: str, text: str, key_seq_1: str, key_seq_2="", key_seq_3="", key_seq_4="", tip=""):
        if action := self.get_action(ident):
            key_sequences = [QKeySequence(key_seq_1)]
            if key_seq_2:
                key_sequences.append(QKeySequence(key_seq_2))
            if key_seq_3:
                key_sequences.append(QKeySequence(key_seq_3))
            if key_seq_4:
                key_sequences.append(QKeySequence(key_seq_4))
            action.setShortcuts(key_sequences)
            if tip:
                action.setToolTip(tip)
            if text:
                action.setText(text)

    def get_action(self, ident: str) -> Optional[QAction]:
        action_name = "action_"+ident
        if hasattr(self.parent,action_name):
            return getattr(self.parent, action_name)
        return None

    def get_action_info(self, ident: str) -> Optional[Tuple[str, str, str]]:
        """
        Returns a tulpe with the action's: shortcut key(s), short description, and tool tip.
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


