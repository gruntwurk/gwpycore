from gwpycore.gui.gui_theme import GWAssets
from typing import Union
from pathlib import Path
import logging
from gwpycore.windows.windows_fonts import WindowsFontInstaller
from gwpycore.core.environ import is_windows
from gwpycore.core.exceptions import GWValueError, GWError


LOG = logging.getLogger("gwpy")


class FontAssets(GWAssets):
    """
    A utility for discovering and loading any font assets associated with the application.

    font_specs = FontAssets("C:/app/assets/fonts")
    """

    def __init__(self, asset_path: Union[Path, str]) -> None:
        super().__init__(asset_path)
        self._font_asset_dict = {}
        self.load_new_fonts()

    def apply_theme(self):
        # No themes for fonts (yet)
        pass

    @property
    def font_list(self) -> dict:
        if not self._font_asset_dict:
            self._font_asset_dict = self.discover_assets()
        return self._font_asset_dict

    def discover_assets(self):
        """
        Scan the font assets folder for all font files.
        Subfolders are assumed to be a font family.

        :return: A dictionary keyed by the font file's name (e.g. "arial.ttf"
                 no path) where the value is a 3-tuple: (font file (full Path),
                 font family (per the subfolder), and the long name of the file
                 ("Undetermined" to start).
        """
        font_dict = {}
        for family_folder in self.asset_path.iterdir():
            if family_folder.is_dir():
                family_name = family_folder.name
                for font_file in family_folder.iterdir():
                    if font_file.is_file() and font_file.suffix in [".ttf", ".otf"]:
                        font_dict[font_file.name] = (font_file, family_name, 'Undetermined')
        return font_dict

    def load_new_fonts(self):
        """Load any fonts that the system doesn't already have installed."""
        if not is_windows():
            raise GWError("Font assets currently only work on Windows.")
        for font_key in self.font_list.keys:
            for font_path, family, title in self.font_list[font_key]:
                with WindowsFontInstaller(font_path) as installer:
                    if not installer.font_exists():
                        try:
                            installer.install_font()
                            # update the font title within the 3-tuple
                            title = installer.full_font_name
                            self.font_list[font_key] = (font_path, family, title)
                        except GWValueError:
                            pass
                        except WindowsError:
                            pass


__all_ = ("FontAssets")
