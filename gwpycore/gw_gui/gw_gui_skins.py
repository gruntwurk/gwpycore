from enum import Enum
from PyQt5.QtCore import QSize
from gwpycore.gw_gui.gw_gui_dialogs import ICON_WARNING, InspectionDialog, inform_user
from gwpycore.gw_functions.gw_numeric import next_in_range
import re

import yaml
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from PyQt5.QtGui import QColor, QIcon, QKeySequence, QPalette, QPixmap
from PyQt5.QtWidgets import QAbstractScrollArea, QApplication, QPushButton, QSizePolicy, QTableWidgetItem, qApp
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
QPALETTE_SLUGS = {
 "window": "base00",
 "windowtext": "base05",
 "base": "base01",
 "alternatebase": "base02",
 "text": "base05",
 "tooltipbase": "base01",
 "tooltiptext": "base04",
 "placeholdertext": "base03",
 "button": "base09",
 "buttontext": "base0A",
 "brighttext": "base06",
 "light": "base05",
 "midlight": "base04",
 "dark": "base01",
 "mid": "base02",
 "shadow": "base00",
 "highlight": "base02",
 "highlightedtext": "base08",
 "link": "base0D",
 "linkvisited": "base0E"}

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

    def __init__(
        self,
        asset_path: Union[Path, str],
        custom_color_map: Optional[Dict[str, tuple]] = None,
        **kwds
    ):
        super().__init__(asset_path, **kwds)
        self.theme_structure = ThemeStructure.SKIN
        self.skin_meta: ThemeMetaData = None
        self.conf_name = "skin.conf"
        self.custom_color_map = custom_color_map
        self.css_name = "style.qss"
        self.qt_gui_palette= QPalette()
        self.skin_list = [x for x in self.themes().keys()]
        self.skin_list.insert(0,"default")
        self.current_skin = 0

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
                self.base16 = yaml.load(f.read())
            self._qt_palette_per_base16()
        else:
            parser = GWConfigParser()
            parser.parse_file(skin_file)

            self.base16 = {}
            # We'll load the Base16 section first (if there is one), because the
            # Skin section can refer to the base16 definitions.
            section = "Base16"
            if parser.has_section(section):
                for option, _ in parser.items(section):
                    self.base16[option] = parser[section].getqcolor(option)
                if len(self.base16) != 16:
                    raise GruntWurkConfigError(f"Expected 16 colors in the [Base16] section but only found {len(self.base16)}.")
                self._qt_palette_per_base16()

            section = "Skin"
            if parser.has_section(section):
                for option in parser.items(section):
                    if option not in QPALETTE_SLUGS:
                        LOG.warning(
                            f"Skin theme '{self.theme_name}' refers to an element '{option}' that doesn't exist."
                        )
                self._qt_palette_per_conf(section, parser)

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

    def _qt_palette_per_conf(self, section, parser):
        def color_choice(option, default) -> QColor:
            c = str(parser[section].gettext(option)).lower()
            if re.match(r"base0[0-9a-f]",c):
                color = self.base16[option]
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



    def _qt_palette_per_base16(self):
        for base_number in self.base16.keys():
            if (not base_number.startswith('base0')) or isinstance(self.base16[base_number], QColor):
                continue
            self.base16[base_number] = QColor(f"#{self.base16[base_number]}")

        pal = self.qt_gui_palette
        pal.setColor(QPalette.Window, self.base16[QPALETTE_SLUGS["window"]])
        pal.setColor(QPalette.WindowText, self.base16[QPALETTE_SLUGS["windowtext"]])
        pal.setColor(QPalette.Base, self.base16[QPALETTE_SLUGS["base"]])
        pal.setColor(QPalette.AlternateBase, self.base16[QPALETTE_SLUGS["alternatebase"]])
        pal.setColor(QPalette.Text, self.base16[QPALETTE_SLUGS["text"]])
        pal.setColor(QPalette.ToolTipBase, self.base16[QPALETTE_SLUGS["tooltipbase"]])
        pal.setColor(QPalette.ToolTipText, self.base16[QPALETTE_SLUGS["tooltiptext"]])
        pal.setColor(QPalette.Button, self.base16[QPALETTE_SLUGS["button"]])
        pal.setColor(QPalette.ButtonText, self.base16[QPALETTE_SLUGS["buttontext"]])
        pal.setColor(QPalette.BrightText, self.base16[QPALETTE_SLUGS["brighttext"]])
        pal.setColor(QPalette.Highlight, self.base16[QPALETTE_SLUGS["highlight"]])
        pal.setColor(QPalette.HighlightedText, self.base16[QPALETTE_SLUGS["highlightedtext"]])
        pal.setColor(QPalette.Link, self.base16[QPALETTE_SLUGS["link"]])
        pal.setColor(QPalette.LinkVisited, self.base16[QPALETTE_SLUGS["linkvisited"]])
        pal.setColor(QPalette.PlaceholderText, self.base16[QPALETTE_SLUGS["placeholdertext"]])
        pal.setColor(QPalette.Light, self.base16[QPALETTE_SLUGS["light"]])
        pal.setColor(QPalette.Midlight, self.base16[QPALETTE_SLUGS["midlight"]])
        pal.setColor(QPalette.Dark, self.base16[QPALETTE_SLUGS["dark"]])
        pal.setColor(QPalette.Mid, self.base16[QPALETTE_SLUGS["mid"]])
        pal.setColor(QPalette.Shadow, self.base16[QPALETTE_SLUGS["shadow"]])

    def _cycle_skin(self, increment=1):
        self.current_skin = next_in_range(self.current_skin, increment, len(self.skin_list)-1)
        self.set_theme(self.skin_list[self.current_skin])
        self.apply_theme()
        self.apply_qss()
        LOG.debug(f"self.qt_gui_palette.color(QPalette.BrightText) = {self.qt_gui_palette.color(QPalette.BrightText).name()}")
        if self.on_change:
            self.on_change(self.qt_gui_palette.color(QPalette.BrightText))
        if hasattr(qApp.activeWindow(), "statusBar"):
            (skin,author) = self.theme_citation()
            qApp.activeWindow().statusBar().showMessage(f"Skin applied: '{skin}' {author}")

    def next_skin(self):
        self._cycle_skin(1)

    def previous_skin(self):
        self._cycle_skin(-1)

    def color_square(self, color, size=64) -> QIcon:
        """
        Returns a QIcon that is a solid square of the named color.
        """
        # TODO add a contrasting border
        pix = QPixmap(QSize(size,size))
        pix.fill(color)
        return QIcon(pix)

    def inspect_skin(self):
        inspector = InspectionDialog(prompt="The current skin is:", buttons=["Previous","Next","Customize"], rows=16, cols=3)
        def display_diagnostic():
            just_default = (self.theme_name == "default") or (not hasattr(self,"base16"))
            if just_default:
                (skin,author) = self.theme_name,""
            else:
                (skin,author) = self.theme_citation()
            inspector.set_name(skin)
            inspector.set_note(author)
            if just_default:
                inspector.info.clear()
            else:
                i=0
                for base_number in self.base16.keys():
                    if not base_number.startswith('base0'):
                        continue
                    if isinstance(self.base16[base_number], QColor):
                        icon = self.color_square(self.base16[base_number])
                        text = self.base16[base_number].name()
                    else:
                        text = f"#{self.base16[base_number]}"
                        icon = self.color_square(QColor(text))
                    inspector.info.setItem(i,0,QTableWidgetItem(base_number))
                    inspector.info.setItem(i,1,QTableWidgetItem(icon, text))
                    slug_list = []
                    for slug in QPALETTE_SLUGS.keys():
                        if QPALETTE_SLUGS[slug] == base_number:
                            slug_list.append(slug)
                    inspector.info.setItem(i,2,QTableWidgetItem(", ".join(slug_list)))
                    i += 1
        def cycle_next():
            self.next_skin()
            display_diagnostic()
        def cycle_previous():
            self.previous_skin()
            display_diagnostic()
        def customize():
            # TODO Implement the Customize button, as described...
            inform_user("The intention of this button is to convert a Base16-only skin from .YAML to .INI. The path of the created INI file will then be placed in the clipboard for further editing. For now, just do it manually.", ICON_WARNING, title="Not Implemented")
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

__all__ = ("QPALETTE_SLUGS", "SkinAssets")
