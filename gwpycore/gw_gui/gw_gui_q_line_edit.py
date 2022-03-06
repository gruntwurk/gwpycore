from PyQt5.QtWidgets import QLineEdit
# TODO Move all PyQT support to a seperate module (gwpyqt)


class QLineEditWithDeselect(QLineEdit):
    def __init__(self, parent=None):
        self.parent = parent
        super(QLineEditWithDeselect, self).__init__(parent)

    # for some reason, the entire existing text (if any) was always selected;
    #  use this method to deselect all and move the cursor to the end
    def focusInEvent(self, e):
        QLineEdit.focusInEvent(self, e)  # do this to show the blinking cursor
        self.deselect()
        self.setCursorPosition(len(self.text()))


__all__ = ("QLineEditWithDeselect",)
