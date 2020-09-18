from PyQt5.QtGui import QIcon, QPixmap
from gwpycore.gw_gui.gw_gui_theme import GWAssets
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData

from typing import Union
from pathlib import Path
from PyQt5.QtWidgets import QStyle, qApp

import logging

LOG = logging.getLogger("main")


class IconAssets(GWAssets):
    """This class manages the content of the assets/icons folder,
    and provides a simple interface for requesting icons. Only icons
    named in the given icon map are handled.

    Icons are loaded on first request, and then cached for further
    requests. Each icon key in the icon_map has a series of fallbacks:
      * The first lookup is in the key-to-file map for the selected icon
        theme. The map is specified in the icons.conf file in the theme
        folder. The map makes it possible to preserve the original file
        name from the icon theme were the icons were extracted.
      * Second, if the icon does not exist in the theme map, the
        GuiIcons class will check if there is a QStyle icon specified in
        the icon_map data tuple[0]. This will let Qt pull the closest
        system icon.
      * Third action is to look up the freedesktop icon theme name using
        the fromTheme Qt call. This generally produces the same results
        as the step above, but has more icons available in other cases.
      * Fourth, and finally, the icon is looked up in the fallback
        folder. Files in this folder must have the same file name as the
        internal icon key, with '-dark' appended to it for
        the dark background version of the icon.
    """

    def __init__(
        self,
        icon_map,
        asset_path: Union[Path, str],
        fallback_theme="fallback-dark",
        exclude=["fallback-dark", "fallback-light"],
    ):
        super().__init__(asset_path)
        self.uses_themes = True

        self.icon_map = icon_map
        self.set_fallback(fallback_theme, exclude)

        self.q_icons = {}
        self.theme_map = {}
        self.theme_list = []
        self.conf_name = "icons.conf"

        self.theme_meta: ThemeMetaData = ""
        LOG.diagnostic(f"System icon theme is '{QIcon.themeName()}'")


    def apply_theme(self):
        """
        Updates the internal theme map.
        (Be sure to call themes() and set_theme() first.)
        """
        self.theme_map = {}

        self.confFile = self.asset_path / self.theme_name / self.conf_name

        parser = GWConfigParser()
        parser.parse_file(self.confFile)
        self.theme_meta = self.fetch_theme_metadata(parser)

        # A conf file is only needed with an icon set if the icon file names
        # don't already match the expected slug names. In that case, a [Map]
        # section is required to map the slug name to the file name.
        section = "Map"
        if parser.has_section(section):
            for slug, icon_file in parser.items(section):
                if slug not in self.icon_map:
                    LOG.warning(
                        f"Theme file refers to an icon name '{slug}' that doesn't exist"
                    )
                else:
                    icon_path: Path = self.asset_path / self.theme_name / icon_file
                    if icon_path.is_file:
                        self.theme_map[slug] = icon_path
                        LOG.diagnostic(f"Icon slot '{slug}' using file '{icon_file}'")
                    else:
                        LOG.error(f"Icon file '{icon_file}' not in theme folder.")

        LOG.info(f"Loaded icon theme '{self.theme_name}'")

    def get_icon(self, slug) -> QIcon:
        """Returns an icon from the icon buffer, loading it first if necessary."""
        if slug in self.q_icons:
            return self.q_icons[slug]
        else:
            q_icon = self._load_icon(slug)
            self.q_icons[slug] = q_icon
            return q_icon

    def flush_icons(self):
        self.q_icons.clear()

    def get_pixmap(self, slug, icon_size) -> QPixmap:
        """Returns an icon as a QPixmap."""
        q_icon = self.get_icon(slug)
        return q_icon.pixmap(icon_size[0], icon_size[1], QIcon.Normal)

    def _load_icon(self, slug) -> QIcon:
        """
        Loads the most appropriate icon associated with the given name (slug).
        Note: "app" is a special slug that refers to the application's icon, which sits outside of the themes.

        The various fallback protocols include:
        - Theme icons before system icons.
        - Prefering svg files over png files.
        """
        if slug not in self.icon_map:
            LOG.error(f"Requested an unknown icon name '{slug}'")
            return QIcon()

        # "app" is a special slug that refers to the application's icon, which sits outside of the themes
        if slug == "app":
            return QIcon(self.asset_path / "application.ico")

        # First choice: From the chosen theme
        # (a) -- as mapped (if there is a conf file with a map)
        if slug in self.theme_map:
            LOG.diagnostic(
                f"Loading: {self.theme_map[slug].relative_to(self.asset_path)}"
            )
            return QIcon(self.theme_map[slug])

        # (b) -- by searching the chosen theme's folder for a name that matches the slug
        icon = self._search_for_icon_file(slug, self.theme_name)
        if icon:
            return icon

        # Second choice: a Qt style icon
        if self.icon_map[slug][0] is not None:
            LOG.diagnostic("Loading icon '%s' from Qt QStyle.standardIcon" % slug)
            return qApp.style().standardIcon(self.icon_map[slug][0])

        # Third choice: from the system theme
        if self.icon_map[slug][1] is not None:
            LOG.diagnostic("Loading icon '%s' from system theme" % slug)
            if QIcon().hasThemeIcon(self.icon_map[slug][1]):
                return QIcon().fromTheme(self.icon_map[slug][1])

        # Ultimate fallback
        icon = self._search_for_icon_file(slug, self.fallback_theme )
        if icon:
            return icon

        # Give up and return an empty icon
        LOG.warning(f"Did not load an icon for '{slug}'")
        return QIcon()

    def _search_for_icon_file(self, slug, theme_name) -> QIcon:
        for suffix in [".svg", ".png", ".jpg"]:
            filepath: Path = self.asset_path / theme_name / (slug + suffix)
            if filepath.is_file:
                LOG.diagnostic(
                    f"Loading icon '{slug}{suffix}' from '{theme_name}' theme"
                )
                return QIcon(str(filepath))


__all__ = ("DEFAULT_ICON_MAP", "IconAssets")