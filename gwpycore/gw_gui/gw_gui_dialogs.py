"""
Frequently Used Message Dialog Boxes
"""
from PyQt5.QtCore import QCoreApplication, QObject, Qt, QTimer
from PyQt5.QtWidgets import QMessageBox

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


__all__ = ("inform_user_about_issue", "ask_user_to_confirm", "ICON_ERROR", "ICON_WARN", "ICON_INFO", "ICON_QUESTION", "STD_DIALOG_OPTS")
