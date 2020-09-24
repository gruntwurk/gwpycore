from argparse import ArgumentParser, Namespace
from typing import Optional
import sys
from pathlib import Path

from gwpycore import (
    QPALETTE_SLUGS,
    basic_cli_parser,
    parse_config,
    setup_logging,
    SkinAssets,
    IconAssets,
)
from PyQt5 import uic

from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import (
    QColor,
    QFont,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextListFormat,
)
from PyQt5.QtWidgets import (
    QStyle,
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog, QTextEdit,
    qApp,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

import logging
from gwpycore import GWStandardEditorApp

LOG = logging.getLogger("main")

ICON_MAP = {
    "about": ("action_About", None, None),
    "bug_report": ("action_Bug_Report", None, None),
    "calendar": ("action_Date", None, None),
    "colors": ("action_Font_Color", None, None),
    "download_cloud": ("action_Updates", None, None),
    "edit_bold": ("action_Edit_Bold", None, None),
    "edit_copy": ("action_Edit_Copy", None, None),
    "edit_cut": ("action_Edit_Cut", None, None),
    "edit_delete": ("", QStyle.SP_DialogDiscardButton, "edit-delete"),
    "edit_italic": ("action_Edit_Italic", None, None),
    "edit_paste": ("action_Edit_Paste", None, None),
    "edit_redo": ("action_Edit_Redo", None, None),
    "edit_underline": ("action_Edit_Underline", None, None),
    "edit_undo": ("action_Edit_Undo", None, None),
    "export_pdf": ("action_Export_Pdf", None, None),
    "file_close": ("action_File_Close", QStyle.SP_DialogCloseButton, "window-close"),
    "file_new": ("action_File_New", None, None),
    "file_open": ("action_File_Open", QStyle.SP_DirOpenIcon, "folder-open"),
    "file_save": ("action_File_Save", QStyle.SP_DialogSaveButton, "document-save"),
    "file_save_as": ("action_File_Save_As", None, None),
    "font": ("action_Font", None, None),
    "full_screen": ("action_Distraction_Free", None, None),
    "hashtag": ("action_Hashtag", None, None),
    "help": ("action_Help", None, None),
    "journal": ("action_New_Entry", None, None),
    "newspaper": ("action_Publication", None, None),
    "preview": ("action_Print_Preview", None, None),
    "print": ("action_Print", None, None),
    "quit": ("action_Quit", None, None),
    "search": ("action_Search", None, "edit-find"),
    "search_replace": ("", None, "edit-find-replace"),
    "select_all": ("action_Select_All", None, None),
    "time": ("action_Time", None, None),
    "word_wrap": ("", None, None),
}

(DialogSpec, BaseClass) = uic.loadUiType("examples/style_test.ui")


class DemoWindow(BaseClass, DialogSpec, GWStandardEditorApp):
    def __init__(self, parent, config, **kwds):
        BaseClass.__init__(self)
        DialogSpec.__init__(self)
        GWStandardEditorApp.__init__(self, **kwds)
        self.parent = parent
        self.config = config
        self.setupUi(self)
        self.setup_assets()
        # Many of the actions (including some of the standard actions in CoreActions)
        # need to know which control is the main text editing control.
        self.edit_control: QTextEdit = self.textEdit_2
        self.connect_actions()
        self.statusBar()


        self.tree1.expandAll()

        # For demo purposes, force devmode on
        self.config.devmode = True
        self.menu_Debug.menuAction().setVisible(self.config.devmode)

    def setup_assets(self):
        self.root_asset_path = Path("examples/assets")
        self.icons = IconAssets(
            ICON_MAP,
            asset_path=self.root_asset_path / "icons",
            fallback_theme="noun-black",
            exclude=[],
            parent=self
        )
        self.setWindowIcon(self.icons.get_icon("app"))
        self.skins = SkinAssets(asset_path=self.root_asset_path / "skins")
        self.skins.connect_on_change(self.set_icon_color)
        self.reload_icons()

    def set_icon_color(self, color: QColor):
        self.icons.colorize(color)
        self.reload_icons()

    def reload_icons(self):
        """
        Load/reload the icons, via the IconAssets manager, according to the map.
        """
        self.icons.set_action_icons_per_map()
        # Icons with alternate states have to be loaded mannually
        self.action_Word_Wrap.setIcon(self.icons.get_icon("word_wrap", on="word_wrap_on"))

    def connect_actions(self):
        self.connect_standard_actions()
        self.action_Date.triggered.connect(self.not_implemented)
        self.action_Search.triggered.connect(self.not_implemented)
        self.action_Hashtag.triggered.connect(self.not_implemented)
        self.action_Time.triggered.connect(self.not_implemented)

    def closeEvent(self, e):
        e.accept()


__version__ = "0.0.1"

CONFIG: Namespace


def load_command_line(args) -> Namespace:
    parser: ArgumentParser = basic_cli_parser(
        version_text=__version__, devel=True, trace=True, logfile=True, configfile=True
    )
    switches = parser.parse_args(args)  # noqa F811
    if switches.logfile:
        switches.logfile = Path(switches.logfile)
    if switches.configfile:
        switches.configfile = Path(switches.configfile)
    return switches  # noqa F811


def further_initialization():
    LOG.trace("Performing further initialization")
    CONFIG.application_title = "Asset Management Demonstration"
    CONFIG.version = __version__

    if CONFIG.devmode:
        LOG.info("Running in dev mode.")
        # TODO special setup for dev mode (e.g. suppressing actual web service calls, not actually sending any emails)


def finish(exitcode=0, exception: Optional[Exception] = None):
    LOG.trace("Finishing")
    if exception:
        exitcode = 1
        if hasattr(exception, "exitcode"):
            exitcode = exception.exitcode
        LOG.uncaught(exception)
    LOG.diagnostic(f"Exit code = {exitcode}")


def start_gui(CONFIG) -> int:
    LOG.trace("Starting up the GUI")
    q_app = QApplication([])
    GUI = DemoWindow(q_app, CONFIG)
    GUI.show()
    return q_app.exec_()


def load_config(configfile: Path, initial_config: Namespace = None) -> Namespace:
    LOG.trace("Loading config")
    parser = parse_config(LOG, configfile)
    config = initial_config if initial_config else Namespace()

    config.serif_typeface = "Times New Roman"
    config.sans_typeface = "Arial"
    if parser.has_section("display"):
        config.serif_typeface = parser["display"].gettext(
            "serif_typeface", config.serif_typeface
        )
        config.sans_typeface = parser["display"].gettext(
            "sans_typeface", config.sans_typeface
        )
    LOG.debug(f"config = {config}")
    return config


def main():
    global CONFIG, LOG
    switches = load_command_line(sys.argv[1:])
    LOG = setup_logging(
        loglevel=switches.loglevel, logfile=switches.logfile, nocolor=switches.nocolor
    )
    LOG.trace("(Previously) Loaded command line and set up logging.")
    # try:
    CONFIG = load_config(configfile=Path(switches.configfile), initial_config=switches)
    further_initialization()
    x = start_gui(CONFIG)
    finish(exitcode=x)
    # except Exception as e:
    #     finish(exception=e)


if __name__ == "__main__":
    main()