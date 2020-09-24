from PyQt5.QtCore import QSize
from gwpycore.gw_gui.gw_gui_svg import colorized_qicon
from PyQt5.QtGui import QColor, QIcon, QPixmap
from gwpycore.gw_gui.gw_gui_theme import GWAssets, ThemeStructure
from gwpycore.gw_basis.gw_config import GWConfigParser
from gwpycore.gw_gui.gw_gui_theme import ThemeMetaData

from typing import List, Optional, Union
from pathlib import Path
from PyQt5.QtWidgets import QAction, QStyle, qApp

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
        fallback_theme: str,
        exclude=[],
        parent=None,
    ):
        super().__init__(asset_path)
        self.parent = parent
        self.theme_structure = ThemeStructure.ICON_SET

        self.icon_map = icon_map
        self.set_fallback(fallback_theme, exclude)
        self.q_icons = {}
        self.theme_map = {}
        self.theme_list = []
        self.conf_name = "icons.conf"
        self.is_colorizable = False
        self.colorize_color = None
        self.theme_meta: ThemeMetaData = None
        LOG.diagnostic(f"System icon theme is '{QIcon.themeName()}'")
        self.theme_name = fallback_theme
        self.apply_theme()

    def colorize(self, color: Optional[QColor]):
        """
        Sets the color for all icons (if the icon set is colorizable).
        """
        if self.is_colorizable and (self.colorize_color != color):
            self.flush_icons()
            self.colorize_color = color

    def colorize_the_color_palette_icon(self, action: QAction, color):
        """
        Changes the icon associated with the given color-palette action to one
        that is a solid block of the given color.
        """
        size: QSize = action.icon().actualSize(self.parent,QSize(64,64))
        pix = QPixmap(size)
        pix.fill(color)
        action.setIcon(QIcon(pix))

    def apply_theme(self):
        """
        Updates the internal theme map.
        (Be sure to call themes() and set_theme() first.)
        """
        self.is_colorizable = self.theme_name.endswith("-black")
        self.theme_map = {}

        self.icon_set_path = self.asset_path / self.theme_name
        conf_file = None
        for child in self.icon_set_path.glob("*.conf"):
            conf_file = child
            break

        if conf_file:
            # A conf file is only needed with an icon set if the icon file names
            # don't already match the expected slug names. In that case, a [Map]
            # section is required to map the slug name to the file name.
            parser = GWConfigParser()
            parser.parse_file(conf_file)
            self.theme_meta = self.fetch_theme_metadata(parser)
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
                        else:
                            LOG.error(f"Icon file '{icon_file}' not in theme folder.")

        LOG.info(f"Loaded icon theme '{self.theme_name}'")

    def get_icon(self, slug, on="", disabled="", active="") -> QIcon:
        """Returns an icon from the icon buffer, loading it first if necessary."""
        if slug in self.q_icons:
            return self.q_icons[slug]
        q_icon = self._load_icon(slug, on, disabled, active)
        self.q_icons[slug] = q_icon
        return q_icon

    def set_action_icons_per_map(self):
        for slug in self.icon_map.keys():
            (action_name,_,_) = self.icon_map[slug]
            LOG.debug(f"self.icon_map[{slug}] = {action_name}")
            if action_name:
                action = self.parent.findChild(QAction,action_name)
                if action:
                    action.setIcon(self.get_icon(slug))


    def flush_icons(self):
        self.q_icons.clear()

    def get_pixmap(self, slug, icon_size) -> QPixmap:
        """Returns an icon as a QPixmap."""
        q_icon = self.get_icon(slug)
        return q_icon.pixmap(icon_size[0], icon_size[1], QIcon.Normal)

    def _load_icon(self, slug, on="", disabled="", active="") -> QIcon:
        """
        Loads the most appropriate icon associated with the given name (slug).
        Note: "app" is a special slug that refers to the application's icon, which sits outside of the themes.

        The various fallback protocols include:
        - Theme icons before system icons.
        - Prefering svg files over png files.
        """
        # "app" is a special slug that refers to the application's icon, which sits outside of the themes
        if slug == "app":
            return QIcon(str(self.asset_path / "application.ico"))

        if slug not in self.icon_map:
            raise Exception(f"Requested an unknown icon name '{slug}'")
            # LOG.error(f"Requested an unknown icon name '{slug}'")
            # return QIcon()

        # First choice: From the chosen theme
        # (a) -- as mapped (if there is a conf file with a map)
        if slug in self.theme_map:
            return colorized_qicon(self.theme_map[slug], color=self.colorize_color, on_path=self.theme_map[on], disabled_path=self.theme_map[disabled], active_path=self.theme_map[active])

        # (b) -- by searching the chosen theme's folder for a name that matches the slug
        icon = self.search_for_icon_file(slug, self.theme_name, on=on, disabled=disabled, active=active)
        if icon:
            return icon

        # Second choice: a Qt style icon
        icon = self.icon_map[slug][1]
        if icon:
            return qApp.style().standardIcon(icon)

        # Third choice: from the system theme
        icon = self.icon_map[slug][2]
        if icon:
            if QIcon().hasThemeIcon(icon):
                return QIcon().fromTheme(icon)

        # Ultimate fallback
        if self.fallback_theme and self.fallback_theme != self.theme_name:
            icon = self.search_for_icon_file(slug, self.fallback_theme, on=on, disabled=disabled, active=active)
            if icon:
                return icon

        # Give up and return an empty icon
        LOG.warning(f"Did not load an icon for '{slug}'")
        return QIcon()

    def search_for_icon_file(self, slug, theme_name, on="", disabled="", active="") -> QIcon:
        slug_path = ""
        on_path = ""
        disabled_path = ""
        active_path = ""
        for suffix in [".svg", ".png", ".jpg"]:
            filepath: Path = self.asset_path / theme_name / (slug + suffix)
            if filepath.is_file:
                slug_path = str(filepath)
                break
        if not slug_path:
            return None
        if on:
            for suffix in [".svg", ".png", ".jpg"]:
                filepath: Path = self.asset_path / theme_name / (on + suffix)
                if filepath.is_file:
                    on_path = str(filepath)
                    break
        if disabled:
            for suffix in [".svg", ".png", ".jpg"]:
                filepath: Path = self.asset_path / theme_name / (disabled + suffix)
                if filepath.is_file:
                    disabled_path = str(filepath)
                    break
        if active:
            for suffix in [".svg", ".png", ".jpg"]:
                filepath: Path = self.asset_path / theme_name / (active + suffix)
                if filepath.is_file:
                    active_path = str(filepath)
                    break
        return colorized_qicon(slug_path, color=self.colorize_color, on_path=on_path, disabled_path=disabled_path, active_path=active_path)

__all__ = ("IconAssets",)