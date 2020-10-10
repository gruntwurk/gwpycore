from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap

def color_subdued(color: QColor):
    """
    Returns a darker/lighter version of the given color that is suitable to use as a background color
    (e.g. pink for red, light gray for dark gray, and vice versa).
    """
    is_dark = color.value() < 128
    if is_dark:
        return color.lighter(250)
    else:
        return color.darker(400)

def color_contrast(color: QColor):
    """
    Returns a stark contrast to the given color.
    """
    h = color.hsvHue() - 180
    if h < 0:
        h += 360
    s = max(color.hsvSaturation(),128)
    v = max(color.value(),128)
    return QColor.fromHsv(h,s,v)

def color_outline(color: QColor):
    """
    Returns either black or white, depending on if the given color is light or dark
    (e.g. to outline it in case the original color is hard to see).
    """
    is_dark = color.value() < 128
    return QColor("white") if is_dark else QColor("black")

def color_square(color: QColor, size=64) -> QIcon:
    """
    Returns a QIcon that is an outlined solid square of the named color.
    """
    r = QRect(0,0,size-1,size-1)
    pix = QPixmap(QSize(size,size))
    painter = QPainter(pix)
    painter.fillRect(r,color)
    painter.setPen(color_outline(color))
    painter.drawRect(r)
    painter.end()
    return QIcon(pix)

__all__ = ("color_subdued", "color_contrast", "color_outline", "color_square")