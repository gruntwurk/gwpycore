import re
import yaml
from gwpycore.gw_functions.gw_numeric import next_in_range
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import GWAssets, ThemeStructure, ThemeMetaData
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, qApp
from pathlib import Path
from typing import Dict, Optional, Union
import logging

LOG = logging.getLogger("main")


class SyntaxAssets(GWAssets):
    """
    If you pass in an existing color map, then the colors loaded from
    the [Syntax] section will be restricted to the keywords named.
    Otherwise, all of the keywords in the section will be assumed valid.
    color_map = {
        "background": (0,0,0),
        "text": (0,0,0),
        "link": (0,0,0),
        "headertext": (0,0,0),
        ...
        }
    """

    def __init__(
        self,
        asset_path: Union[Path, str],
        color_map: Optional[Dict[str, tuple]] = None,
    ):
        super().__init__(asset_path)
        self.theme_structure = ThemeStructure.SYNTAX
        self.conf_name = "syntax.conf"
        self.color_map = color_map
        self.syntax_meta: ThemeMetaData = None

    def apply_theme(self):
        """
        Note: Call themes() and set_theme() before calling apply_theme().
        """
        if not self.theme_name:
            return
        syntax_file = self.asset_path / self.theme_name / "syntax.conf"

        parser = GWConfigParser()
        parser.parse_file(syntax_file)

        self.syntax_meta = self.fetch_theme_metadata(parser)

        section = "Syntax"
        if parser.has_section(section):
            for option in parser.items(section):
                if option not in self.color_map:
                    LOG.warning(
                        f"Syntax theme {self.theme_name} refers to a syntax element '{option}' that doesn't exist."
                    )
                else:
                    self.color_map[option] = parser[section].getcolor(option)
        LOG.info(f"Loaded syntax theme '{self.theme_name}'")

    def _cycle_syntax_scheme(self, increment=1):
        self.current_syntax_scheme = next_in_range(
            self.current_syntax_scheme, increment, len(self.syntax_scheme_list) - 1
        )
        theme_name = self.syntax_scheme_list[self.current_syntax_scheme]
        self.set_theme(theme_name)
        self.apply_theme()
        self.apply_qss()
        if self.on_change:
            self.on_change(self.qt_gui_palette.color(QPalette.BrightText))
        qApp.activeWindow().statusBar().showMessage(
            f"Now using the '{theme_name}' syntax_scheme."
        )

    def next_syntax_scheme(self):
        self._cycle_syntax_scheme(1)

    def previous_syntax_scheme(self):
        self._cycle_syntax_scheme(-1)


__all__ = ("SyntaxAssets",)