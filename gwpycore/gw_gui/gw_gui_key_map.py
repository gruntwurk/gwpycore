from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QObject
from typing import Any, Optional
from ..gw_basis.gw_exceptions import GruntWurkConfigError
import csv
import logging

LOG = logging.getLogger('main')

class AppActions:
    """
    A builder/container for the various QActions needed by a Qt application.
    Actions can be built individually by calling addAction().
    Actions can be built in bulk by calling loadKeyMap(), which parses a CSV source for the settings.
    All of the actions built can then be referenced as attributes of this class instance.
    """

    def __init__(self, parent: Optional[QObject]) -> None:
        self.parent = parent
        self.actionDict = {}

    def addAction(self, ident: str, text: str, key_seq_1: str, key_seq_2="", key_seq_3="", key_seq_4="", tip=""):
        if ident in self.actionDict:
            action = self.actionDict[ident]
        else:
            action = QAction(text, self.parent)
            self.actionDict[ident] = action
        key_sequences = [QKeySequence(key_seq_1)]
        if (key_seq_2):
            key_sequences.append(QKeySequence(key_seq_2))
        if (key_seq_3):
            key_sequences.append(QKeySequence(key_seq_3))
        if (key_seq_4):
            key_sequences.append(QKeySequence(key_seq_4))
        action.setShortcuts(key_sequences)
        action.setToolTip(tip)

    def attachActions(self):
        """
        Attaches all of the actions to the parent.
        Be sure to wait until after all of the actions have been defined and/or overwritten before calling this.
        """
        if (self.parent):
            for ident in self.actionDict:
                self.attachAction(ident)

    def attachAction(self, ident):
        LOG.debug(f"attaching ident = {ident}")
        self.parent.addAction(self.actionDict[ident])


    def loadKeyMapFile(self, filepath: str):
        """
        throws: GruntWurkConfigError
        """
        with open(filepath, newline='') as csvfile:
            self.loadKeyMapData(csvfile, init_mode=False)

    def loadKeyMapData(self, data, init_mode):
        """
        data -- a list of strings (or anything else that csv.reader() accepts)
        init_mode -- Use True to signal that this is the initial load, which dictates
            what the action identifiers are, or False to verify that the action
            identifiers already exist.
        throws: GruntWurkConfigError
        """
        if (not init_mode):
            keymap = csv.reader(data)
            bad_idents = []
            for i, row in enumerate(keymap):
                if i > 0:
                    ident = row[0]
                    if not ident in self.actionDict:
                        bad_idents.append(ident)
            if bad_idents:
                bad_idents_str = ", ".join(bad_idents)
                raise GruntWurkConfigError(f"Invalid key mapping. No such action identifier(s) as {bad_idents_str}.")
            data.seek(0)

        keymap = csv.reader(data)
        for i, row in enumerate(keymap):
            # check the header row
            if i == 0:
                if row != ["Action Identifier", "Action Label", "Key Seq 1", "Key Seq 2", "Key Seq 3", "Key Seq 4", "Tip"]:
                    raise GruntWurkConfigError('Invalid key map. The header line must be "Action Identifier,Action Label,Key Seq 1,Key Seq 2,Key Seq 3,Key Seq 4,Tip" exactly.')
            else:
                self.addAction(*row)

    def __getattr__(self, name: str) -> Any:
        return self.actionDict[name]


_ALL_ = ("AppActions")
