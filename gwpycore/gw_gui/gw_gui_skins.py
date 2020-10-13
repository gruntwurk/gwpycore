from enum import Enum, IntEnum
from gwpycore.gw_functions.gw_colors import color_parse, color_square, color_subdued
from PyQt5.QtCore import QSize
from gwpycore.gw_gui.gw_gui_dialogs import ICON_WARNING, InspectionDialog, inform_user
from gwpycore.gw_functions.gw_numeric import next_in_range
import re

import yaml
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from PyQt5.QtGui import QColor, QIcon, QKeySequence, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QPushButton,
    QSizePolicy,
    QTableWidgetItem,
    qApp,
)
from gwpycore.gw_gui.gw_gui_theme import GWAssets, ThemeStructure
from pathlib import Path
from typing import Dict, Optional, Union
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData
import logging

LOG = logging.getLogger("main")

# FIXME Radio button and checkbox icons are stubbornly black & white and do not match the theme
# FIXME The title bars (MS Windows) do not match the theme
# FIXME When returning to the default scheme, the alternate base is messed up
# FIXME The tab borders are awkwardly colored (padding vs. margin?)
# FIXME The buttons in a button box have black shadows even with dark themes.

# IMPORTANT: Hex digits A-F must be upper case
DEFAULT_COLOR_MAPPING = {
    "window": "base00",
    "windowtext": "base05",
    "base": "base01",
    "alternatebase": "base02",
    "text": "base05",
    "tooltipbase": "base01",
    "tooltiptext": "base04",
    "button": "base09",
    "buttontext": "base0A",
    "brighttext": "base06",
    "highlight": "base02",
    "highlightedtext": "base08",
    "link": "base0D",
    "linkvisited": "base0E",
    "placeholdertext": "base03",
    "light": "base05",
    "midlight": "base04",
    "dark": "base01",
    "mid": "base02",
    "shadow": "base00",
    "icons": "base06",
}

SKIN_QSS = """
QWindow, QMainWindow, .QToolBar, .QToolButton, .QToolBar::separator {
    background-color: palette(base);
}
.QToolBar::handle, .QToolBar::separator {
    color: palette(window-text);
}
QMenuBar, QMenu, QMenu::separator {
    color: palette(window-text);
    background-color: palette(window);
    border: 2px solid palette(window);
}
QMenuBar::item:selected {
    background-color: palette(button);
}
QStatusBar, QTabWidget, QTabWidget QWidget {
    background-color: palette(window);
}
QTabWidget::pane {
    border: 0 3px 3px 0 solid palette(mid);
}
.QTabBar::tab {
    background-color: palette(window);
    border: 2px palette(mid) solid;
    border-bottom: 2px palette(base) solid;
    margin: 4px;
}
.QTabBar::tab:selected, .QTabBar::tab:hover {
    background-color: palette(base);
    border: 2px palette(dark) solid;
    border-bottom: 2px palette(base) solid;
}
QDialog, QAbstractButton, QDockWidget, QHeaderView::section, QLabel {
    background-color: palette(window);
}
QTreeView {
    background-color: palette(window);
    alternate-background-color: palette(alternate-base);
    selection-color: palette(highlighted-text);
    selection-background-color: palette(highlight);
}
.QDialogButtonBox::menu-button {
    background-color: palette(button);
}
.QComboBox, .QDateTimeEdit, .QLCDNumber, .QTextEdit, .QLineEdit {
    background-color: palette(base);
    color: palette(window-text);
    border: 1px solid palette(shadow);
}
.QScrollBar {
    background-color: palette(dark);
}
.QProgressBar {
    background-color: palette(dark);
    border: 2px solid palette(button);
    border-radius: 5px;
    text-align: center;
    color: palette(text);
}
.QProgressBar::chunk {
    background-color: palette(midlight);
    width: 20px;
    margin: 0.5px;
}
"""


class SkinAssets(GWAssets):
    """
    Handles the overall look and feel of an application.

    The colors loaded from the [Skin] section will be restricted to the
    QPalette properties.

    If you pass in an existing custom color map, then the colors loaded from
    the [Custom] section will be restricted to the keywords named.
    Otherwise, all of the keywords in the section will be assumed valid.
    custom_color_map = {
        "treewordcount": (0,0,0),
        "statusnone": (0,0,0),
        "statusunsaved": (0,0,0),
        "statussaved": (0,0,0)
        }
    """

    def __init__(self,asset_path: Union[Path, str],custom_color_map = {},**kwds):
        super().__init__(asset_path, **kwds)
        self.theme_structure = ThemeStructure.SKIN
        self.skin_meta: ThemeMetaData = None
        self.conf_name = "skin.conf"
        self.css_name = "style.qss"
        self.skin_list = [x for x in self.themes().keys()]
        self.skin_list.insert(0, "default")
        self.current_skin = 0
        self.custom_color_map = custom_color_map
        self.reset_color_map()

    def reset_color_map(self):
        self.color_map = {}
        self.color_map.update(DEFAULT_COLOR_MAPPING)
        self.color_map.update(self.custom_color_map)
        pal = QApplication.style().standardPalette()
        self.color_names = {}
        self.color_names[self.color_map["window"]] = pal.window()
        self.color_names[self.color_map["windowtext"]] = pal.windowText()
        self.color_names[self.color_map["base"]] = pal.base()
        self.color_names[self.color_map["alternatebase"]] = pal.alternateBase()
        self.color_names[self.color_map["text"]] = pal.text()
        self.color_names[self.color_map["tooltipbase"]] = pal.toolTipBase()
        self.color_names[self.color_map["tooltiptext"]] = pal.toolTipText()
        self.color_names[self.color_map["button"]] = pal.button()
        self.color_names[self.color_map["buttontext"]] = pal.buttonText()
        self.color_names[self.color_map["brighttext"]] = pal.brightText()
        self.color_names[self.color_map["highlight"]] = pal.highlight()
        self.color_names[self.color_map["highlightedtext"]] = pal.highlightedText()
        self.color_names[self.color_map["link"]] = pal.link()
        self.color_names[self.color_map["linkvisited"]] = pal.linkVisited()
        self.color_names[self.color_map["placeholdertext"]] = pal.placeholderText()
        self.color_names[self.color_map["light"]] = pal.light()
        self.color_names[self.color_map["midlight"]] = pal.midlight()
        self.color_names[self.color_map["dark"]] = pal.dark()
        self.color_names[self.color_map["mid"]] = pal.mid()
        self.color_names[self.color_map["shadow"]] = pal.shadow()

    def apply_qss(self):
        """
        """
        css_data = SKIN_QSS
        if self.theme_name and self.css_name:
            self.css_file = self.asset_path / self.theme_name / self.css_name
            try:
                if self.css_file.is_file():
                    with self.css_file.open(mode="r", encoding="utf8") as inFile:
                        css_data += inFile.read()
            except Exception as e:
                LOG.error(f"Could not load theme CSS file {e}")
                return
        qApp.setStyleSheet(css_data)

    def apply_theme(self, theme_name):
        """
        (First, call themes() to see what's available.)
        """
        if not self._set_theme(theme_name):
            return    # already set, nothing to do

        # self.apply_qss()

        self.reset_color_map()
        if self.theme_name == "default":
            return

        self.skin_meta: ThemeMetaData = self.themes()[self.theme_name]
        skin_file = Path(self.skin_meta.filename)
        if self.skin_meta.filename.endswith(".yaml"):
            self.apply_base16_theme(skin_file)
        else:
            self.apply_conf_theme(skin_file)

        LOG.info(f"Loaded skin theme '{self.theme_name}'")
        self._qt_palette_per_color_map()

    def apply_base16_theme(self, skin_file):
        with skin_file.open("r") as f:
            self.color_names = yaml.load(f.read())
            del self.color_names["scheme"]
            del self.color_names["author"]
        self.post_process_colors()

    def apply_conf_theme(self, skin_file):
        parser = GWConfigParser()
        parser.parse_file(skin_file)

        self.color_names = {}
        # We'll load the ColorNames section first (if there is one), because the
        # ColorMap section can refer to the named colors.
        section = "ColorNames"
        if parser.has_section(section):
            for option, _ in parser.items(section):
                self.color_names[option] = color_parse(parser[section].gettext(option))

        section = "ColorMap"
        if parser.has_section(section):
            for option in parser.items(section):
                if option not in self.color_map:
                    LOG.warning(
                        f"Skin theme '{self.theme_name}' refers to a ColorMap element '{option}' that doesn't exist."
                    )
                self.color_map[option] = color_parse(parser[section].gettext(option), names= self.color_names)

    def _qt_palette_per_color_map(self):
        pal = QApplication.style().standardPalette()
        pal.setColor(QPalette.Window, self.color_map["window"])
        pal.setColor(QPalette.WindowText, self.color_map["windowtext"])
        pal.setColor(QPalette.Base, self.color_map["base"])
        pal.setColor(QPalette.AlternateBase, self.color_map["alternatebase"])
        pal.setColor(QPalette.Text, self.color_map["text"])
        pal.setColor(QPalette.ToolTipBase, self.color_map["tooltipbase"])
        pal.setColor(QPalette.ToolTipText, self.color_map["tooltiptext"])
        pal.setColor(QPalette.Button, self.color_map["button"])
        pal.setColor(QPalette.ButtonText, self.color_map["buttontext"])
        pal.setColor(QPalette.BrightText, self.color_map["brighttext"])
        pal.setColor(QPalette.Highlight, self.color_map["highlight"])
        pal.setColor(QPalette.HighlightedText, self.color_map["highlightedtext"])
        pal.setColor(QPalette.Link, self.color_map["link"])
        pal.setColor(QPalette.LinkVisited, self.color_map["linkvisited"])
        pal.setColor(QPalette.PlaceholderText, self.color_map["placeholdertext"])
        pal.setColor(QPalette.Light, self.color_map["light"])
        pal.setColor(QPalette.Midlight, self.color_map["midlight"])
        pal.setColor(QPalette.Dark, self.color_map["dark"])
        pal.setColor(QPalette.Mid, self.color_map["mid"])
        pal.setColor(QPalette.Shadow, self.color_map["shadow"])
        qApp.setPalette(pal)

    def post_process_colors(self):
        """If the values in self.color_names and self.color_map haven't been converted from strings to QColors yet, do so now."""
        for name in self.color_names.keys():
            self.color_names[name] = color_parse(self.color_names[name])
        for key in self.color_map.keys():
            self.color_map[key] = color_parse(self.color_map[key], self.color_names)

    def _cycle_skin(self, increment=1):
        self.current_skin = next_in_range(
            self.current_skin, increment, len(self.skin_list) - 1
        )
        self.apply_theme(self.skin_list[self.current_skin])
        self.apply_qss()

        if self.on_change:
            self.on_change(self.color_map["icons"])
        if hasattr(qApp.activeWindow(), "statusBar"):
            (skin, author) = self.theme_citation()
            qApp.activeWindow().statusBar().showMessage(
                f"Skin applied: '{skin}' {author}"
            )

    def next_skin(self):
        self._cycle_skin(1)

    def previous_skin(self):
        self._cycle_skin(-1)

    def inspect_skin(self):
        inspector = InspectionDialog(
            prompt="The current skin is:",
            buttons=["Previous", "Next", "Customize"],
            rows=16,
            cols=4,
        )
        inspector.info.horizontalHeader().show()
        inspector.info.setHorizontalHeaderLabels(
            ["Name", "Color", "Used for", "Over a Computed Background"]
        )

        def display_diagnostic():
            just_default = (self.theme_name == "default")
            if just_default:
                (skin, author) = self.theme_name, ""
            else:
                (skin, author) = self.theme_citation()
            inspector.set_name(skin)
            inspector.set_note(author)
            if just_default:
                inspector.info.clear()
                return

            i = 0
            # FIXME Any mappings that have directly set colors (not going through a named color) are not included here
            for name in self.color_names.keys():
                inspector.info.setItem(i, 0, QTableWidgetItem(name))

                color = self.color_names[name]
                if isinstance(color, QColor):
                    text = color.name()
                else:
                    text = f"#{color}"
                    color = QColor(text)
                icon = color_square(color)
                inspector.info.setItem(i, 1, QTableWidgetItem(icon, text))

                slug_list = []
                for slug in self.color_map.keys():
                    if DEFAULT_COLOR_MAPPING[slug] == name:
                        slug_list.append(slug)
                if not slug_list:
                    slug_list.append("(not used)")
                item = QTableWidgetItem(", ".join(slug_list))
                inspector.info.setItem(i, 2, item)

                scolor = color_subdued(color)
                stext = scolor.name()
                item = QTableWidgetItem(f"{text}  ->  {stext}")
                item.setForeground(color)
                item.setBackground(scolor)
                inspector.info.setItem(i, 3, item)

                i += 1

        def cycle_next():
            self.next_skin()
            display_diagnostic()

        def cycle_previous():
            self.previous_skin()
            display_diagnostic()

        def customize():
            # TODO Implement the Customize button, as described...
            inform_user(
                "The intention of this button is to convert a Base16-only skin from .YAML to .INI. The path of the created INI file will then be placed in the clipboard for further editing. For now, just do it manually.",
                ICON_WARNING,
                title="Not Implemented",
            )

        btn_next = inspector.button("next")
        btn_next.setShortcut(QKeySequence("F9"))
        btn_next.pressed.connect(cycle_next)
        btn_previous = inspector.button("previous")
        btn_previous.setShortcut(QKeySequence("Ctrl+F9"))
        btn_previous.pressed.connect(cycle_previous)
        btn_customize = inspector.button("customize")
        btn_customize.pressed.connect(customize)
        display_diagnostic()
        inspector.exec_()


__all__ = ("SkinAssets",)
