from gwpycore.gw_gui.gw_gui_images import ImageAssets
from gwpycore.gw_gui.gw_gui_fonts import FontAssets
from gwpycore.gw_gui.gw_gui_syntax import SyntaxHighlightAssets
from gwpycore.gw_gui.gw_gui_icons import IconAssets
from gwpycore.gw_gui.gw_gui_dialogs import ask_user_to_choose
from gwpycore.gw_gui.gw_gui_skins import SkinAssets
from os import path
from PyQt5.QtWidgets import QStyle, qApp

import logging

LOG = logging.getLogger("main")

DEFAULT_ICON_MAP = {
    # Project and GUI icons (QT icon, System icon)
    "novelwriter": (None, None),
    "cls_none": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_novel": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_plot": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_character": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_world": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_timeline": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_object": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_entity": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_custom": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_archive": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "cls_trash": (QStyle.SP_DriveHDIcon, "drive-harddisk"),
    "proj_document": (QStyle.SP_FileIcon, "x-office-document"),
    "proj_folder": (QStyle.SP_DirIcon, "folder"),
    "proj_orphan": (QStyle.SP_MessageBoxWarning, "dialog-warning"),
    "proj_nwx": (None, None),
    "status_lang": (None, None),
    "status_time": (None, None),
    "status_stats": (None, None),
    "doc_h1": (QStyle.SP_FileIcon, "x-office-document"),
    "doc_h2": (QStyle.SP_FileIcon, "x-office-document"),
    "doc_h3": (QStyle.SP_FileIcon, "x-office-document"),
    "doc_h4": (QStyle.SP_FileIcon, "x-office-document"),
    "search_case": (None, None),
    "search_regex": (None, None),
    "search_word": (None, None),
    "search_loop": (None, None),
    "search_project": (None, None),
    "search_cancel": (None, None),
    "search_preserve": (None, None),
    ## General Button Icons
    "folder-open": (QStyle.SP_DirOpenIcon, "folder-open"),
    "delete": (QStyle.SP_DialogDiscardButton, "edit-delete"),
    "close": (QStyle.SP_DialogCloseButton, "window-close"),
    "done": (QStyle.SP_DialogApplyButton, None),
    "clear": (QStyle.SP_LineEditClearButton, "clear_left"),
    "save": (QStyle.SP_DialogSaveButton, "document-save"),
    "add": (None, "list-add"),
    "remove": (None, "list-remove"),
    "search": (None, "edit-find"),
    "search-replace": (None, "edit-find-replace"),
    "edit": (None, None),
    "check": (None, None),
    "cross": (None, None),
    "hash": (None, None),
    "maximise": (None, None),
    "minimise": (None, None),
    "refresh": (None, None),
    "reference": (None, None),
    "backward": (None, None),
    "forward": (None, None),
    ## Switches
    "sticky-on": (None, None),
    "sticky-off": (None, None),
    "bullet-on": (None, None),
    "bullet-off": (None, None),
}


class ExampleMain:
    def __init__(self) -> None:
        self.custom_color_map = {
            "treewordcount": (0,0,0),
            "statusnone": (0,0,0),
            "statusunsaved": (0,0,0),
            "statussaved": (0,0,0),
            "helptext": (0,0,0)
            }
        self.syntax_color_map = {
            "background": (0,0,0),
            "text": (0,0,0),
            "link": (0,0,0),
            "headertext": (0,0,0),
        }

        LOG.debug("Enter: SkinAssets")
        self.skins = SkinAssets(asset_path = "./assets/skins", custom_color_map = self.custom_color_map)
        index = ask_user_to_choose("Please pick a skin", self.skins.themes())
        if index >=0:
            self.skins.set_theme(self.skins.themes()[index])
            self.skins.apply_theme()

        LOG.debug("Enter: IconAssets")
        self.icons = IconAssets(asset_path = "./assets/icons", icon_map = DEFAULT_ICON_MAP,
            fallback_theme="fallback-dark",
            exclude=["fallback-dark", "fallback-light"])
        index = ask_user_to_choose("Please pick an icon set", self.icons.themes())
        if index >=0:
            self.icons.set_theme(self.icons.themes()[index])
            self.icons.apply_theme()


        LOG.debug("Enter: SyntaxHighlightAssets")
        self.syntaxes = SyntaxHighlightAssets(asset_path = "./assets/syntax", color_map = self.syntax_color_map)
        index = ask_user_to_choose("Please pick a syntax color theme", self.syntaxes.themes())
        if index >=0:
            self.syntaxes.set_theme(self.syntaxes.themes()[index])
            self.syntaxes.apply_theme()

        LOG.debug("Enter: FontAssets")
        self.fonts = FontAssets(asset_path = "./assets/fonts")
        self.fonts.load_new_fonts()

        self.image_map = {}
        LOG.debug("Enter: ImageAssets")
        self.images = ImageAssets(asset_path = "./assets/images", image_map = self.image_map)
        # pix: QPixmap = self.images.load_image("foo")


        self.getIcon = self.icons.get_icon
        self.getPixmap = self.icons.get_pixmap
        self.loadDecoration = self.images.load_image

        # Extract Other Info
        self.guiDPI = qApp.primaryScreen().logicalDotsPerInchX()
        self.guiScale = qApp.primaryScreen().logicalDotsPerInchX() / 96.0
        self.mainConf.guiScale = self.guiScale
        LOG.verbose("GUI DPI: %.1f" % self.guiDPI)
        LOG.verbose("GUI Scale: %.2f" % self.guiScale)

        self.update_dependant_colors()

    def update_dependant_colors(self):
        back_color = qApp.palette().window().Color()
        text_color = qApp.palette().windowText().Color()
        back_light_color = back_color.lightnessF()
        text_light_color = text_color.lightnessF()

        if back_light_color > text_light_color:
            help_light_color = text_light_color + 0.65 * (back_light_color - text_light_color)
        else:
            help_light_color = back_light_color + 0.65 * (text_light_color - back_light_color)

        self.help_text_color = [int(255 * help_light_color)] * 3

        return True


if __name__ == "__main__":
    x = ExampleMain()