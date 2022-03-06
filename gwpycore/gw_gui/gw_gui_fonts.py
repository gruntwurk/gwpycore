from gwpycore.gw_gui.gw_gui_theme import GWAssets
from math import ceil
from typing import List, NamedTuple, Union
from collections import namedtuple
from PyQt5.QtGui import QFont, QFontMetrics, QFontDatabase
from pathlib import Path
from PyQt5.QtWidgets import qApp
import logging
# TODO Move all PyQT support to a seperate module (gwpyqt)

LOG = logging.getLogger("main")

BasicFontMetrics = namedtuple(
    "BasicFontMetrics", "points, pixels, icon_size, n_height, n_width", defaults=[0.0,0,0,0,0]
)


class FontAssets(GWAssets):
    """
    A utility for discovering and loading any font assets associated with the application.

    font_specs = FontAssets("C:/app/assets/fonts")
    """

    def __init__(self, asset_path: Union[Path, str]) -> None:
        super().__init__(asset_path)

        self.gui_font_db = QFontDatabase()
        self.load_new_fonts()
        self.gui_font = qApp.font()
        self.gui_font_fixed = QFontDatabase.systemFont(QFontDatabase.FixedFont)

    def apply_theme(self):
        # No themes for fonts
        pass

    def font_asset_list(self):
        """Scan the font assets folder for all the subfolders (each assumed to be a font family)."""
        if self.available_font_families:
            return self.available_font_families
        for child in self.asset_path.iterdir():
            if child.is_dir():
                self.available_font_families.append(child.name)
        return self.available_font_families

    def load_new_fonts(self):
        """Load any fonts that the system doesn't already have installed."""
        new_fonts = []
        for family in self.font_asset_list():
            font_dir: Path = self.asset_path / family
            if font_dir.is_dir:
                if family not in self.gui_font_db.families():
                    for child in font_dir.iterdir():
                        if child.is_file() and child.suffix in [".ttf", ".otf"]:
                            new_fonts.append(child)
        new_font: Path
        for new_font in new_fonts:
            LOG.diagnostic(f"Loading font asset: {new_font.relative_to(self.asset_path)}")
            id = self.gui_font_db.addApplicationFont(new_font)
            if id < 0:
                LOG.error(
                    f"Failed to add font: {new_font.relative_to(self.asset_path)}"
                )
        return

    def basic_font_metrics(self, font: QFont) -> BasicFontMetrics:
        """
        Calculates some commonly needed font metrics and returns them in a
        BasicFontMetrics tuple.
        """
        qMetric = QFontMetrics(font)
        info = BasicFontMetrics.make(
            [
                font.pointSizeF(),
                qMetric.height(),
                qMetric.ascent(),
                qMetric.boundingRect("N").height(),
                qMetric.boundingRect("N").width(),
            ]
        )

        LOG.diagnostic("GUI Font Family: %s" % font.family())
        LOG.diagnostic("GUI Font Point Size: %.2f" % info.points)
        LOG.diagnostic("GUI Font Pixel Size: %d" % info.pixels)
        LOG.diagnostic("GUI Base Icon Size: %d" % info.icon_size)
        LOG.diagnostic("Text 'N' Height: %d" % info.n_height)
        LOG.diagnostic("Text 'N' Width: %d" % info.n_width)
        return info

    def get_text_width(self, font: QFont, proposed_text):
        """Calculates the width needed to contain a given piece of text."""
        return int(ceil(QFontMetrics(font).boundingRect(proposed_text).width()))


__all_ = ("FontAssets", "BasicFontMetrics")
