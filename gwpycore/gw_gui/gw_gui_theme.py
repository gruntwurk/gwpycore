from abc import ABC, abstractmethod
from gwpycore.gw_basis.gw_exceptions import GruntWurkConfigError
from pathlib import Path
from gwpycore.gw_basis.gw_config import GWConfigParser

from os import path
from typing import List, Optional, Tuple, Dict, Union
from collections import namedtuple

from PyQt5.QtWidgets import QStyle, qApp


import logging

LOG = logging.getLogger("main")

Color = Optional[Tuple[int, int, int]]

ThemeMetaData = namedtuple(
    "ThemeMetaData",
    "name description author credit url license license_url ",
    defaults=["", "", "", "", "", "", ""],
)


class GWAssets(ABC):
    """
    Base class for the various asset-management classes (SkinAssets, IconAssets, ImageAssets,
    FontAssets, SyntaxHighlightAssets).
    Some of these have user-selectable themes: SkinAssets, IconAssets, and SyntaxHighlightAssets.

    ?? style.qss
    """
    def __init__(self, asset_path: Union[Path,str]):
        if isinstance(asset_path, Path):
            self.asset_path = asset_path
        else:
            self.asset_path = Path(asset_path)
        if not self.asset_path.is_dir():
            raise GruntWurkConfigError(f"{asset_path} is not a directory or does not exist.")

        self.uses_themes = False
        self.theme_name = ""
        self.fallback_theme = ""
        self.excluded_themes = []
        self.available_themes: Dict[str,ThemeMetaData] = []

        self.conf_name = "theme.conf"

    def set_theme(self, theme_name):
        """
        Declare which theme should be used. (Call themes() to see what's avalailble.)
        """
        if not self.uses_themes:
            raise GruntWurkConfigError("Attempted to set a theme name for an asset class that doesn't use themes.")
        self.theme_name = theme_name

    @abstractmethod
    def apply_theme(self):
        pass

    def set_fallback(self, fallback_theme: str, excluded_themes: List[str] = []):
        """
        If the asset has a fallback theme, name it here.
        If there are multiple fallback asset folders, then list them in the exclusions.
        """
        self.fallback_theme = fallback_theme
        if excluded_themes:
            self.excluded_themes = excluded_themes
        else:
            self.excluded_themes = [fallback_theme]

    def theme_metadata(self):
        """
        Returns the ThemeMetaData tuple for the currently set theme.
        """
        if not self.uses_themes:
            raise GruntWurkConfigError("Attempted to retrieve theme data for an asset class that doesn't use themes.")
        if self.theme_name:
            return self.available_themes[self.theme_name]
        else:
            return ThemeMetaData()

    def themes(self) -> Dict[str,ThemeMetaData]:
        """
        Scans the themes folder and returns a dictionary of all available themes
        (excluding any fallbacks), along with their metadata.
        """
        if not self.uses_themes:
            raise GruntWurkConfigError("Attempted to retrieve theme data for an asset class that doesn't use themes.")
        if self.available_themes:
            return self.available_themes

        self.available_themes = self.find_themes(self.asset_path, self.conf_name)
        for fallback in self.excluded_themes:
            if fallback in self.available_themes:
                del self.available_themes[fallback]
        if self.theme_name not in self.available_themes:
            self.theme_name = ""
        return self.available_themes

    def fetch_theme_metadata(self, parser: GWConfigParser) -> ThemeMetaData:
        theme_meta = ThemeMetaData
        section="Main"
        theme_meta.name = parser[section].gettext("name", "")
        theme_meta.description = parser[section].gettext("description", "")
        theme_meta.author = parser[section].gettext("author", "")
        theme_meta.credit = parser[section].gettext("credit", "")
        theme_meta.url = parser[section].gettext("url", "")
        theme_meta.license = parser[section].gettext("license", "")
        theme_meta.license_url = parser[section].gettext("licenseurl", "")
        return theme_meta

    def find_themes(self,
        theme_base: Path, config_file_name="theme.conf"
    ) -> Dict[str, ThemeMetaData]:
        """
        Scans the specified folder for any subfolders containing a file of the given config_file_name.
        Returns a dictionary where the key is the name of the subfolder and the
        associated value is an instance of the ThemeMetaData named tuple.

        config_file_name -- "theme.conf", "syntax.ini", etc.
        """
        themes = {}
        parser = GWConfigParser()
        for child in theme_base.iterdir():
            if child.is_dir():
                parser.parse_file(child / config_file_name)
                themes[child.name] = self.fetch_theme_metadata(parser)
        return themes



