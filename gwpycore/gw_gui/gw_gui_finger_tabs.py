#'FingerTabs' - Horizontal Text, Horizontal Tabs in PyQt
# Source: https://gist.github.com/LegoStormtroopr/5075267

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QStyle, QStyleOptionTab, QStylePainter, QTabBar, QTabWidget

class FingerTabBarWidget(QTabBar):
    def __init__(self, parent=None, *args, **kwargs):
        self.tabSize = QSize(kwargs.pop('width',100), kwargs.pop('height',25))
        QTabBar.__init__(self, parent, *args, **kwargs)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, Qt.AlignVCenter |\
                             Qt.TextDontClip, \
                             self.tabText(index));
        painter.end()
    def tabSizeHint(self,index):
        return self.tabSize

class FingerTabWidget(QTabWidget):
    """A QTabWidget equivalent which uses our FingerTabBarWidget"""
    def __init__(self, parent, *args):
        QTabWidget.__init__(self, parent, *args)
        self.setTabBar(FingerTabBarWidget(self))


_ALL_ = ("FingerTabWidget", "FingerTabBarWidget")
