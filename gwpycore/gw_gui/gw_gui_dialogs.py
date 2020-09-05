"""
Frequently Used Message Dialog Boxes
"""
from typing import List

from PyQt5.QtCore import QCoreApplication, QObject, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QVBoxLayout)

ICON_ERROR = QMessageBox.Critical
ICON_WARN = QMessageBox.Warning
ICON_INFO = QMessageBox.Information
ICON_QUESTION = QMessageBox.Question
STD_DIALOG_OPTS = Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint


def inform_user_about_issue(message: str, icon: QMessageBox.Icon = ICON_ERROR, parent: QObject = None, title="", timeout=0):
    if title == "":
        title = "Warning" if (icon == ICON_WARN) else "Error"
    if timeout:
        message += f"\n\n(This warning will automatically close in {int(timeout/1000)} seconds.)"
    buttons = QMessageBox.StandardButton(QMessageBox.Ok)
    box = QMessageBox(icon, title, message, buttons, parent, STD_DIALOG_OPTS)
    box.show()
    QCoreApplication.processEvents()
    box.raise_()
    if timeout:
        QTimer.singleShot(timeout, box.close)
    box.exec_()


def ask_user_to_confirm(question: str, icon: QMessageBox.Icon = ICON_QUESTION, parent: QObject = None, title="Please Confirm") -> bool:
    buttons = QMessageBox.StandardButton(QMessageBox.Yes | QMessageBox.No)
    box = QMessageBox(icon, title, question, buttons, parent, STD_DIALOG_OPTS)
    box.setDefaultButton(QMessageBox.No)
    box.show()
    QCoreApplication.processEvents()
    box.raise_()
    return box.exec_() == QMessageBox.Yes


class ChoicesDialog(QDialog):
    def __init__(self, parent=None):
        super(ChoicesDialog, self).__init__(parent)
        self.setModal(True)
        self.question = QLabel("Please choose:")
        self.choices = QComboBox()
        self.cancel_button = QPushButton("Cancel")
        self.select_button = QPushButton("Select")
        # Make the user specifically click the Select button. Hitting Enter might be too easy and set the wrong choice.
        self.select_button.setDefault(False)
        # https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        self.icon_label = QLabel()
        # TODO https://openapplibrary.org/dev-tutorials/qt-icon-themes
        self.icon_label.setWindowIcon(QIcon.fromTheme("dialog-question"))
        layout = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout2.addWidget(self.question)
        layout2.addWidget(self.choices)
        layout2.addWidget(self.select_button)
        layout.addWidget(self.icon_label)
        layout.addLayout(layout2)
        self.setLayout(layout)
        self.cancel_button.clicked.connect(self.reject)
        self.select_button.clicked.connect(self.make_selection)
        self.setStyleSheet(
            """
            QPushButton {font-size:14pt;}
            QComboBox {font-size:14pt;}
            QLabel {font-size:14pt;}
        """
        )

    def make_selection(self):
        # 0 = rejected (Escape), so a positive result needs to be 1-based
        self.done(self.choices.currentIndex() + 1)


def ask_user_to_choose(question: str, choices: List[str], icon: QMessageBox.Icon = ICON_QUESTION, parent: QObject = None, title="Please Make a Selection") -> int:
    box = ChoicesDialog(parent)
    box.setWindowTitle(title)
    box.question.setText(question)
    box.choices.addItems(choices)
    box.show()
    QCoreApplication.processEvents()
    box.raise_()
    return box.exec_()


__all__ = ("inform_user_about_issue", "ask_user_to_confirm", "ask_user_to_choose", "ICON_ERROR", "ICON_WARN", "ICON_INFO", "ICON_QUESTION", "STD_DIALOG_OPTS")
