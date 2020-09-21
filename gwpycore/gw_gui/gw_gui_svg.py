from PyQt5.QtCore import QFileInfo, QObject, QRect, QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QIconEngine, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import qApp
from PyQt5.QtSvg import QSvgRenderer

from typing import TYPE_CHECKING, MutableMapping, Optional, Tuple, Union
import logging

LOG = logging.getLogger("main")


def colorized_qicon(
    path: str, color: Optional[QColor] = None, on_path="", disabled_path="", active_path=""
) -> QIcon:
    """
    Returns a QIcon patched with colorizing methods.
    (QIcons used with Qt's model/view framework can't be subclassed.)
    """
    iconEngine = _IconEngine(path, color=color)
    icon = QIcon(iconEngine)
    icon.addState = iconEngine.addState
    icon.pixmapGenerator = iconEngine.pixmapGenerator
    icon.color = iconEngine.color
    if on_path:
        iconEngine.addState(on_path, mode=QIcon.Normal, state=QIcon.On)
    if disabled_path:
        iconEngine.addState(disabled_path, mode=QIcon.Disabled)
    if active_path:
        iconEngine.addState(active_path, mode=QIcon.Active)
    return icon


class PixmapGenerator(QObject):
    """Renders the SVG image and applies the color."""

    def __init__(self, path: str, color: Optional[QColor] = None, parent=None):
        super(PixmapGenerator, self).__init__(parent=parent)
        self._path = path
        self._color: Optional[QColor] = color
        self._svg_renderer = QSvgRenderer(self._path)

    def path(self) -> str:
        return self._path

    def color(self) -> Optional[QColor]:
        return self._color

    def pixmap(self, size: QSize) -> QPixmap:
        """
        Render the svg file to a QPixmap, applying the color override if applicable.
        """
        # Create a blank canvas
        image = QImage(size, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)

        # Use the QSvgRenderer to draw the image
        painter = QPainter(image)
        self._svg_renderer.render(painter)
        painter.end()

        if self._color:
            # Create a second canvas solidly filled with the color then mask it with the original image
            colorImage = QImage(size, QImage.Format_ARGB32_Premultiplied)
            colorImage.fill(QColor(self._color))
            painter = QPainter(colorImage)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.drawImage(0, 0, image)
            painter.end()
            image = colorImage

        return QPixmap.fromImage(image)


class _IconEngine(QIconEngine):
    """
    A QIconEngine which uses a PixmapGenerator for its work.
    """

    def __init__(self, path: str, color=None):
        super(_IconEngine, self).__init__()
        self._defaultGenerator = PixmapGenerator(path, color=color)
        self._pixmapGenerators = {(QIcon.Normal, QIcon.Off): self._defaultGenerator}

    def __del__(self):
        # Re-implemented to avoid this object being garbage collected unnecessarily
        pass

    def addState(
        self,
        path: str,
        color: Optional[QColor] = None,
        mode: QIcon.Mode = QIcon.Normal,
        state: QIcon.State = QIcon.Off,
    ):
        """Use the provided path and color when an icon is requested for the identified mode and state."""
        color = color or self.color()
        generator = PixmapGenerator(path, color=color)
        self._pixmapGenerators[(mode, state)] = generator

    def pixmapGenerator(self, mode=QIcon.Normal, state=QIcon.Off) -> PixmapGenerator:
        return self._pixmapGenerators.get((mode, state), self._defaultGenerator)

    def color(self, mode=QIcon.Normal, state=QIcon.Off) -> Optional[QColor]:
        return self.pixmapGenerator(mode=mode, state=state).color()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        return self.pixmapGenerator(mode=mode, state=state).pixmap(size)

    def paint(
        self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State
    ):
        painter.drawPixmap(rect.topLeft(), self.pixmap(rect.size(), mode, state))
