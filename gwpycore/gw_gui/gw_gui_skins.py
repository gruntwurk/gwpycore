from gwpycore.gw_functions.gw_numeric import next_in_range
import re

import yaml
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, qApp
from gwpycore.gw_gui.gw_gui_theme import GWAssets, ThemeStructure
from pathlib import Path
from typing import Dict, Optional, Union
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData
import logging

LOG = logging.getLogger("main")

# FIXME Radio button and checkbox icons are stubbornly black & white and do not match the theme
# FIXME The title bars (MS Windows) do not match the theme
# FIXME When retrurning to the default scheme, the alternate base is messed up
# FIXME The tab borders are awkwardly colored (padding vs. margin?)
# FIXME The buttons in a button box have black shadows even with dark themes.



# IMPORTANT: Hex digits A-F must be upper case
QPALETTE_SLUGS = {
 "window": "base00",
 "windowtext": "base05",
 "base": "base01",
 "alternatebase": "base02",
 "text": "base05",
 "tooltipbase": "base01",
 "tooltiptext": "base04",
 "placeholdertext": "base04",
 "button": "base03",
 "buttontext": "base0A",
 "brighttext": "base06",
 "light": "base05",
 "midlight": "base04",
 "dark": "base01",
 "mid": "base02",
 "shadow": "base00",
 "highlight": "base02",
 "highlightedtext": "base0D",
 "link": "base0D",
 "linkvisited": "base0E"}

SKIN_QSS = """
QWindow, QMainWindow {
    background-color: palette(base);
}
QMenuBar, QMenu, QMenu::separator {
    background-color: palette(window);
    border: 2px solid palette(window);
    color: palette(window-text);
}
QMenuBar::item:selected {
    background-color: palette(button);
}
QStatusBar {
    background-color: palette(window);
}
QTabWidget, QTabWidget QWidget {
    background-color: palette(window);
    border-color: palette(mid);
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
.QToolBar, .QToolButton, .QToolBar::separator   {
    background-color: palette(base);
}
.QToolBar::handle, .QToolBar::separator {
    color: palette(window-text);
}
QDockWidget {
    background-color: palette(window);
}
QHeaderView::section {
    background-color: palette(window);
}
QLabel {
    background-color: palette(window);
}
QTreeView {
    background-color: palette(window);
    alternate-background-color: palette(alternate-base);
    selection-color: palette(highlighted-text);
    selection-background-color: palette(highlight);
}
QAbstractButton {
    background-color: palette(window);
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
QDialog {
    background-color: palette(window);
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

    def __init__(
        self,
        asset_path: Union[Path, str],
        custom_color_map: Optional[Dict[str, tuple]] = None
    ):
        super().__init__(asset_path)
        self.theme_structure = ThemeStructure.SKIN
        self.skin_meta: ThemeMetaData = None
        self.conf_name = "skin.conf"
        self.custom_color_map = custom_color_map
        self.css_name = "style.qss"
        self.qt_gui_palette= QPalette()
        self.skin_list = [x for x in self.themes().keys()]
        self.skin_list.insert(0,"default")
        self.current_skin = 0

    def connect_on_change(self, callback):
        self.on_change = callback

    def apply_qss(self):
        """
        """
        css_data = SKIN_QSS
        if self.theme_name and self.css_name:
            self.css_file = self.asset_path / self.theme_name /self.css_name
            try:
                if self.css_file.is_file():
                    with self.css_file.open(mode="r", encoding="utf8") as inFile:
                        css_data += inFile.read()
            except Exception as e:
                LOG.error(f"Could not load theme CSS file {e}")
                return
        qApp.setStyleSheet(css_data)


    def apply_theme(self):
        """
        Note: Call themes() and set_theme() before calling apply_theme().
        """
        # self.apply_qss()

        self.qt_gui_palette =QApplication.style().standardPalette()
        if self.theme_name == "default":
            qApp.setPalette(self.qt_gui_palette)
            return

        self.skin_meta: ThemeMetaData = self.themes()[self.theme_name]
        skin_file = Path(self.skin_meta.filename)
        if self.skin_meta.filename.endswith(".yaml"):
            with skin_file.open("r") as f:
                base16 = yaml.load(f.read())
            self._qt_palette_per_base16(base16)
        else:
            parser = GWConfigParser()
            parser.parse_file(skin_file)

            base16 = {}
            # We'll load the Base16 section first (if there is one), because the
            # Skin section can refer to the base16 definitions.
            section = "Base16"
            if parser.has_section(section):
                for option, _ in parser.items(section):
                    base16[option] = parser[section].getqcolor(option)
                if len(base16) != 16:
                    raise GruntWurkConfigError(f"Expected 16 colors in the [Base16] section but only found {len(base16)}.")
                self._qt_palette_per_base16(base16)

            section = "Skin"
            if parser.has_section(section):
                for option in parser.items(section):
                    if option not in QPALETTE_SLUGS:
                        LOG.warning(
                            f"Skin theme '{self.theme_name}' refers to an element '{option}' that doesn't exist."
                        )
                self._qt_palette_per_conf(section, parser, base16)

            section = "Custom"
            if parser.has_section(section):
                for option in parser.items(section):
                    if option not in self.custom_color_map:
                        LOG.warning(
                            f"Skin theme {self.theme_name} refers to an custom color '{option}' that doesn't exist."
                        )
                    else:
                        self.custom_color_map[option] = parser[section].getcolor(option)

        LOG.info(f"Loaded skin theme '{self.theme_name}'")
        qApp.setPalette(self.qt_gui_palette)

    def _qt_palette_per_conf(self, parser, base16):
        def color_choice(section, option, default) -> QColor:
            c = str(parser[section].gettext(option)).lower()
            if re.match(r"base0[0-9a-f]",c):
                color = base16[option]
                if isinstance(color,QColor):
                    return color
                return QColor(f"#{color}")
            return parser[section].getqcolor(option,default)
        pal = self.qt_gui_palette
        pal.setColor(QPalette.Window, color_choice("window", pal.window))
        pal.setColor(QPalette.WindowText, color_choice("windowtext", pal.windowText))
        pal.setColor(QPalette.Base, color_choice("base", pal.base))
        pal.setColor(QPalette.AlternateBase, color_choice("alternatebase", pal.alternateBase))
        pal.setColor(QPalette.Text, color_choice("text", pal.text))
        pal.setColor(QPalette.ToolTipBase, color_choice("tooltipbase", pal.toolTipBase))
        pal.setColor(QPalette.ToolTipText, color_choice("tooltiptext", pal.toolTipText))
        pal.setColor(QPalette.Button, color_choice("button", pal.button))
        pal.setColor(QPalette.ButtonText, color_choice("buttontext", pal.buttonText))
        pal.setColor(QPalette.BrightText, color_choice("brighttext", pal.brightText))
        pal.setColor(QPalette.Highlight, color_choice("highlight", pal.highlight))
        pal.setColor(QPalette.HighlightedText, color_choice("highlightedtext", pal.highlightedText))
        pal.setColor(QPalette.Link, color_choice("link", pal.link))
        pal.setColor(QPalette.LinkVisited, color_choice("linkvisited", pal.linkVisited))
        pal.setColor(QPalette.PlaceholderText, color_choice("placeholdertext", pal.placeholderText))
        pal.setColor(QPalette.Light, color_choice("light", pal.light))
        pal.setColor(QPalette.Midlight, color_choice("midlight", pal.midlight))
        pal.setColor(QPalette.Dark, color_choice("dark", pal.dark))
        pal.setColor(QPalette.Mid, color_choice("mid", pal.mid))
        pal.setColor(QPalette.Shadow, color_choice("shadow", pal.shadow))



    def _qt_palette_per_base16(self, base16):
        for base_number in base16.keys():
            if (not base_number.startswith('base0')) or isinstance(base16[base_number], QColor):
                continue
            base16[base_number] = QColor(f"#{base16[base_number]}")

        pal = self.qt_gui_palette
        pal.setColor(QPalette.Window, base16[QPALETTE_SLUGS["window"]])
        pal.setColor(QPalette.WindowText, base16[QPALETTE_SLUGS["windowtext"]])
        pal.setColor(QPalette.Base, base16[QPALETTE_SLUGS["base"]])
        pal.setColor(QPalette.AlternateBase, base16[QPALETTE_SLUGS["alternatebase"]])
        pal.setColor(QPalette.Text, base16[QPALETTE_SLUGS["text"]])
        pal.setColor(QPalette.ToolTipBase, base16[QPALETTE_SLUGS["tooltipbase"]])
        pal.setColor(QPalette.ToolTipText, base16[QPALETTE_SLUGS["tooltiptext"]])
        pal.setColor(QPalette.Button, base16[QPALETTE_SLUGS["button"]])
        pal.setColor(QPalette.ButtonText, base16[QPALETTE_SLUGS["buttontext"]])
        pal.setColor(QPalette.BrightText, base16[QPALETTE_SLUGS["brighttext"]])
        pal.setColor(QPalette.Highlight, base16[QPALETTE_SLUGS["highlight"]])
        pal.setColor(QPalette.HighlightedText, base16[QPALETTE_SLUGS["highlightedtext"]])
        pal.setColor(QPalette.Link, base16[QPALETTE_SLUGS["link"]])
        pal.setColor(QPalette.LinkVisited, base16[QPALETTE_SLUGS["linkvisited"]])
        pal.setColor(QPalette.PlaceholderText, base16[QPALETTE_SLUGS["placeholdertext"]])
        pal.setColor(QPalette.Light, base16[QPALETTE_SLUGS["light"]])
        pal.setColor(QPalette.Midlight, base16[QPALETTE_SLUGS["midlight"]])
        pal.setColor(QPalette.Dark, base16[QPALETTE_SLUGS["dark"]])
        pal.setColor(QPalette.Mid, base16[QPALETTE_SLUGS["mid"]])
        pal.setColor(QPalette.Shadow, base16[QPALETTE_SLUGS["shadow"]])

    def _cycle_skin(self, increment=1):
        self.current_skin = next_in_range(self.current_skin, increment, len(self.skin_list)-1)
        theme_name = self.skin_list[self.current_skin]
        self.set_theme(theme_name)
        self.apply_theme()
        self.apply_qss()
        if self.on_change:
            self.on_change(self.qt_gui_palette.color(QPalette.BrightText))
        qApp.activeWindow().statusBar().showMessage(f"Now using the '{theme_name}' skin.")

    def next_skin(self):
        self._cycle_skin(1)

    def previous_skin(self):
        self._cycle_skin(-1)

__all__ = ("QPALETTE_SLUGS", "SkinAssets")