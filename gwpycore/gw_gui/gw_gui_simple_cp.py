import re

from PyQt5.QtCore import QCoreApplication, QLocale, QObject, QRect, QTimer, Qt
from PyQt5.QtWidgets import QCheckBox, QMessageBox, QPushButton, QTextEdit, QWidget


class SimpleControlPanel(QWidget):
    """
    Subclass this to make a quick and dirty dialog box with uniformly sized
    controls that are automatically laid out in a grid (top to bottom,
    left to right).

    Currently defined for cells that are pushbuttons, checkboxes, or read-only
    text (a label).
    """

    def __init__(self, title="Control Panel", grid_width=1, grid_height=15, cell_width=250, cell_height=26, horizontal_margin=10, vertical_margin=5):
        QWidget.__init__(self)
        self.setWindowTitle(title)
        self.central_widget = QWidget(self)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin

        w = grid_width * cell_width + horizontal_margin * 2
        h = grid_height * cell_height + vertical_margin * 3
        self.setMinimumSize(w, h)

        self.current_grid_col = 0
        self.current_grid_row = 0

        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

    def _normalized_name(self, name):
        normalized_name = re.sub(r"[^A-Za-z0-9]+", "", name)
        return normalized_name

    def _cell_geometry(self) -> QRect:
        y = self.current_grid_col * (self.cell_width + self.horizontal_margin) + self.horizontal_margin
        x = self.current_grid_row * (self.cell_height + self.vertical_margin) + self.vertical_margin * 2
        return QRect(y, x, self.cell_width, self.cell_height)

    def add_label(self, name):
        """
        Drop a label (read-only text) in the next cell down.
        """
        txt = QTextEdit(name, self.central_widget)
        txt.setGeometry(self._cell_geometry())
        txt.setAlignment(Qt.AlignCenter)
        txt.setObjectName("txt" + self._normalized_name(name))
        self.move_to_next_cell()
        return txt

    def add_checkbox(self, name, tip=""):
        """
        Drop a checkbox control in the next cell down.
        """
        chk = QCheckBox(self.central_widget)
        chk.setText(name)
        chk.setGeometry(self._cell_geometry())
        chk.setMouseTracking(False)
        chk.setObjectName("chk" + self._normalized_name(name))
        chk.setToolTip(tip if tip else name)
        self.move_to_next_cell()
        return chk

    def add_action_button(self, name, callback, tip=""):
        """
        Drop a pushbutton control in the next cell down.
        """
        btn = QPushButton(self.central_widget)
        btn.setText(name)
        btn.setGeometry(self._cell_geometry())
        btn.setMouseTracking(False)
        btn.setObjectName("btn" + self._normalized_name(name))
        btn.pressed.connect(callback)
        btn.setToolTip(tip if tip else name)
        self.move_to_next_cell()
        return btn

    def move_to_next_cell(self):
        """
        Advance to the next cell down (wrapping to the top of the next column, if needed).
        """
        self.current_grid_row += 1
        if self.current_grid_row >= self.grid_height:
            self.current_grid_col += 1
            self.current_grid_row = 0
            self.resize_to_grid()

    def resize_to_grid(self):
        """
        Resize the dialog box to accomodate the current size of the grid.
        """
        self.grid_width = max(self.grid_width, (self.current_grid_col + 1))
        self.resize(
            self.grid_width * (self.cell_width + self.horizontal_margin) + self.horizontal_margin,
            self.grid_height * (self.cell_height + self.vertical_margin) + self.vertical_margin * 2)


_ALL_ = ("SimpleControlPanel")
