from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import qApp
from gwpycore.gw_gui.gw_gui_theme import GWAssets
from pathlib import Path
from typing import Dict, Optional, Union
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData
import logging

LOG = logging.getLogger("main")

QPALETTE_SLUGS = ["window", "windowtext", "base", "alternatebase", "text", "tooltipbase", "tooltiptext", "placeholdertext", "button", "buttontext", "brighttext", "light", "midlight", "dark", "mid", "shadow", "highlight", "highlightedtext", "link", "linkvisited"]

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
    ):
        super().__init__(asset_path)
        self.uses_themes = True

        self.skin_meta: ThemeMetaData = None
        self.conf_name = "skin.conf"
        self.custom_color_map = custom_color_map
        self.css_name = "style.qss"
        self.qt_gui_palette= QPalette()


    def apply_qss(self):
        """
        """
        if not self.theme_name:
            return
        self.css_file = self.asset_path / self.theme_name /self.css_name
        css_data = ""
        try:
            if self.css_file.is_file():
                with self.css_file.open(mode="r", encoding="utf8") as inFile:
                    css_data = inFile.read()
        except Exception as e:
            LOG.error(f"Could not load theme CSS file {e}")
            return
        qApp.setStyleSheet(css_data)

    def apply_theme(self):
        """
        Note: Call themes() and set_theme() before calling apply_theme().
        """
        self.apply_qss()

        skin_file = self.asset_path / self.theme_name / "skin.conf"
        parser = GWConfigParser(LOG)
        parser.parse_file(skin_file)

        self.skin_meta = self.fetch_theme_metadata(parser)

        s = "Skin"
        if parser.has_section(s):
            for option in parser.items(s):
                if option not in QPALETTE_SLUGS:
                    LOG.warning(
                        f"Skin theme {self.theme_name} refers to an element '{option}' that doesn't exist."
                    )

            pal = self.qt_gui_palette
            pal.setColor(parser[s].getqcolor("window", pal.window))
            pal.setColor(parser[s].getqcolor("windowtext", pal.windowText))
            pal.setColor(parser[s].getqcolor("base", pal.base))
            pal.setColor(parser[s].getqcolor("alternatebase", pal.alternateBase))
            pal.setColor(parser[s].getqcolor("text", pal.text))
            pal.setColor(parser[s].getqcolor("tooltipbase", pal.toolTipBase))
            pal.setColor(parser[s].getqcolor("tooltiptext", pal.toolTipText))
            pal.setColor(parser[s].getqcolor("button", pal.button))
            pal.setColor(parser[s].getqcolor("buttontext", pal.buttonText))
            pal.setColor(parser[s].getqcolor("brighttext", pal.brightText))
            pal.setColor(parser[s].getqcolor("highlight", pal.highlight))
            pal.setColor(parser[s].getqcolor("highlightedtext", pal.highlightedText))
            pal.setColor(parser[s].getqcolor("link", pal.link))
            pal.setColor(parser[s].getqcolor("linkvisited", pal.linkVisited))
            pal.setColor(parser[s].getqcolor("placeholdertext", pal.placeholderText))
            pal.setColor(parser[s].getqcolor("light", pal.light))
            pal.setColor(parser[s].getqcolor("midlight", pal.midlight))
            pal.setColor(parser[s].getqcolor("dark", pal.dark))
            pal.setColor(parser[s].getqcolor("mid", pal.mid))
            pal.setColor(parser[s].getqcolor("shadow", pal.shadow))
        qApp.setPalette(self.gui_palette)

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

