import re
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import qApp
from gwpycore.gw_gui.gw_gui_theme import GWAssets
from pathlib import Path
from typing import Dict, Optional, Union
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData
import logging

LOG = logging.getLogger("main")


QPALETTE_SLUGS_LIGHT = {"window": "base00",
 "windowtext": "base05",
 "base": "base01",
 "alternatebase": "base02",
 "text": "base05",
 "tooltipbase": "base01",
 "tooltiptext": "base04",
 "placeholdertext": "base04",
 "button": "base03",
 "buttontext": "base0a",
 "brighttext": "base06",
 "light": "base05",
 "midlight": "base04",
 "dark": "base01",
 "mid": "base02",
 "shadow": "base00",
 "highlight": "base02",
 "highlightedtext": "base0d",
 "link": "base0d",
 "linkvisited": "base0e"}

QPALETTE_SLUGS_DARK = {"window": "base00",
 "shadow": "base07",
 "base": "base06",
 "dark": "base06",
 "tooltipbase": "base06",
 "highlight": "base05",
 "mid": "base05",
 "alternatebase": "base05",
 "button": "base04",
 "tooltiptext": "base03",
 "placeholdertext": "base03",
 "midlight": "base03",
 "windowtext": "base02",
 "light": "base02",
 "text": "base02",
 "brighttext": "base01",
 "buttontext": "base0a",
 "highlightedtext": "base0d",
 "link": "base0d",
 "linkvisited": "base0e"}


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
        parser = GWConfigParser()
        parser.parse_file(skin_file)

        self.skin_meta = self.fetch_theme_metadata(parser)
        # slug_map = QPALETTE_SLUGS_DARK if self.theme_name.endswith("-dark") else QPALETTE_SLUGS_LIGHT
        slug_map = QPALETTE_SLUGS_LIGHT

        # We'll load the Base16 section first (if there is one), because the
        # Skin section can refer to the base16 definitions.
        s = "Base16"
        if parser.has_section(s):
            base16 = {}
            for option, _ in parser.items(s):
                base16[option] = parser[s].getqcolor(option)
            if len(base16) != 16:
                raise GruntWurkConfigError(f"Expected 16 colors in the [Base16] section but only found {len(base16)}.")
            pal = self.qt_gui_palette
            pal.setColor(QPalette.Window, base16[slug_map["window"]])
            pal.setColor(QPalette.WindowText, base16[slug_map["windowtext"]])
            pal.setColor(QPalette.Base, base16[slug_map["base"]])
            pal.setColor(QPalette.AlternateBase, base16[slug_map["alternatebase"]])
            pal.setColor(QPalette.Text, base16[slug_map["text"]])
            pal.setColor(QPalette.ToolTipBase, base16[slug_map["tooltipbase"]])
            pal.setColor(QPalette.ToolTipText, base16[slug_map["tooltiptext"]])
            pal.setColor(QPalette.Button, base16[slug_map["button"]])
            pal.setColor(QPalette.ButtonText, base16[slug_map["buttontext"]])
            pal.setColor(QPalette.BrightText, base16[slug_map["brighttext"]])
            pal.setColor(QPalette.Highlight, base16[slug_map["highlight"]])
            pal.setColor(QPalette.HighlightedText, base16[slug_map["highlightedtext"]])
            pal.setColor(QPalette.Link, base16[slug_map["link"]])
            pal.setColor(QPalette.LinkVisited, base16[slug_map["linkvisited"]])
            pal.setColor(QPalette.PlaceholderText, base16[slug_map["placeholdertext"]])
            pal.setColor(QPalette.Light, base16[slug_map["light"]])
            pal.setColor(QPalette.Midlight, base16[slug_map["midlight"]])
            pal.setColor(QPalette.Dark, base16[slug_map["dark"]])
            pal.setColor(QPalette.Mid, base16[slug_map["mid"]])
            pal.setColor(QPalette.Shadow, base16[slug_map["shadow"]])
        qApp.setPalette(self.qt_gui_palette)

        s = "Skin"
        if parser.has_section(s):
            for option in parser.items(s):
                if option not in slug_map:
                    LOG.warning(
                        f"Skin theme {self.theme_name} refers to an element '{option}' that doesn't exist."
                    )

            def color_choice(option, default):
                c = str(parser[s].gettext(option)).lower()
                if re.match(r"base0[0-9a-f]",c):
                    return base16[option]
                return parser[s].getqcolor(option,default)

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
        qApp.setPalette(self.qt_gui_palette)

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

