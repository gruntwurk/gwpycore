from argparse import ArgumentParser
from gwpycore.gw_gui.gw_gui_syntax import SyntaxAssets
from gwpycore import ConfigSettings, GWConfigParser
from typing import Optional
import sys
from pathlib import Path

from gwpycore import (
    basic_cli_parser,
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

CONFIG = ConfigSettings()

# Note: LOG will get re-defined in main(). This is a temporary placeholder.
LOG = logging.getLogger("main")

__version__ = "0.0.1"


# This icon map does three things:
#
#   1. It lists all of the icons used by the application. (The dict key is
#      the icon's "slug").
#   2. Tuple[0] associates the icon with its corresponding QAction object (by
#      the action name, with a prefix of "action_" assumed).
#   3. Tuple[1] and Tuple[2] optionally provide fallback icons from the QStyle
#      icons and the system theme, respectively.
#
# For icons with alternate states ("off", "on", "disabled", etc.), only list
# the primary ("off") icon here. But then, also edit reload_icons(), below,
# to have it manually load the icon as an icon bundle.
ICON_MAP = {
    "about": ("about", None, None),
    "bug_report": ("report_bug", None, None),
    "calendar": ("date", None, None),
    "colors": ("font_color", None, None),
    "download_cloud": ("updates", None, None),
    "edit_bold": ("edit_bold", None, None),
    "edit_copy": ("edit_copy", None, None),
    "edit_cut": ("edit_cut", None, None),
    "edit_delete": ("", QStyle.SP_DialogDiscardButton, "edit-delete"),
    "edit_italic": ("edit_italic", None, None),
    "edit_paste": ("edit_paste", None, None),
    "edit_redo": ("edit_redo", None, None),
    "edit_underline": ("edit_underline", None, None),
    "edit_undo": ("edit_undo", None, None),
    "export_pdf": ("export_pdf", None, None),
    "file_close": ("file_close", QStyle.SP_DialogCloseButton, "window-close"),
    "file_new": ("file_new", None, None),
    "file_open": ("file_open", QStyle.SP_DirOpenIcon, "folder-open"),
    "file_save": ("file_save", QStyle.SP_DialogSaveButton, "document-save"),
    "file_save_as": ("file_save_as", None, None),
    "font": ("font", None, None),
    "full_screen": ("distaction_free", None, None),
    "hashtag": ("hashtag", None, None),
    "help": ("help", None, None),
    "journal": ("new_entry", None, None),
    "newspaper": ("publication", None, None),
    "preview": ("print_preview", None, None),
    "print": ("print", None, None),
    "quit": ("quit", None, None),
    "search": ("search", None, "edit-find"),
    "search_replace": ("", None, "edit-find-replace"),
    "select_all": ("select_all", None, None),
    "time": ("time", None, None),
    "hide": ("", None, None),
    "show": ("", None, None),
    "word_wrap": ("", None, None),
}

(DialogSpec, BaseClass) = uic.loadUiType("examples/assets_demo.ui")


class DemoWindow(BaseClass, DialogSpec, GWStandardEditorApp):
    def __init__(self, parent, **kwds):
        BaseClass.__init__(self)
        DialogSpec.__init__(self)
        GWStandardEditorApp.__init__(self, **kwds)
        self.parent = parent
        self.setupUi(self)
        self.setup_assets()
        # Many of the actions (including some of the standard actions in CoreActions)
        # need to know which control is the main text editing control.
        self.edit_control: QTextEdit = self.textEdit_2
        self.connect_actions()
        self.statusBar()

        self.tree1.expandAll()

        self.menu_Debug.menuAction().setVisible(CONFIG.devmode)

    def setup_assets(self):
        self.set_asset_root("examples/assets")
        self.icons = IconAssets(
            ICON_MAP,
            asset_path= self.asset_root() / "icons",
            fallback_theme="noun-black",
            exclude=[],
            parent=self
        )
        self.setWindowIcon(self.icons.get_icon("app"))
        self.skins = SkinAssets(asset_path= self.asset_root() / "skins")
        self.skins.connect_on_change(self.set_icon_color)
        self.reload_icons()
        self.syntax_schemes = SyntaxAssets(asset_path= self.asset_root() / "syntax")

    def set_icon_color(self, color: QColor):
        self.icons.colorize(color)
        self.reload_icons()

    def reload_icons(self):
        """
        Load/reload the icons, via the IconAssets manager, according to the map.
        """
        self.icons.set_action_icons_per_map()
        # Icons with alternate states have to be loaded manually
        self.action_word_wrap.setIcon(self.icons.get_icon("word_wrap", on="word_wrap_on"))
        self.action_hide_menu.setIcon(self.icons.get_icon("hide", on="show"))

    def connect_actions(self):
        self.connect_standard_actions()
        self.action_date.triggered.connect(self.not_implemented)
        self.action_search.triggered.connect(self.not_implemented)
        self.action_hashtag.triggered.connect(self.not_implemented)
        self.action_time.triggered.connect(self.not_implemented)
        self.keep_actions_active()

    def closeEvent(self, e):
        e.accept()




def load_command_line(args):
    """
    Parses the command-line switches and adds the corresponding values to CONFIG.
    """
    parser: ArgumentParser = basic_cli_parser(
        version_text=__version__, devel=True, trace=True, logfile=True, configfile=True
    )
    switches = parser.parse_args(args)  # noqa F811

    # Convert any path strings to Path()
    if switches.logfile:
        switches.logfile = Path(switches.logfile)
    if switches.configfile:
        switches.configfile = Path(switches.configfile)

    CONFIG.update(switches)


def further_initialization():
    LOG.trace("Performing further initialization")
    CONFIG.application_title = "Asset Management Demonstration"
    CONFIG.version = __version__

    # For demo purposes, force devmode on
    CONFIG.devmode = True
    if CONFIG.devmode:
        LOG.info("Running in dev mode.")
        # TODO special setup for dev mode (e.g. suppressing actual web service calls, not actually sending any emails)
        # Note: In DemoWindow.__init__, the visibility of the Debug menu is determined by the dev mode.

def finish(exitcode=0, exception: Optional[Exception] = None):
    LOG.trace("Finishing")
    if exception:
        exitcode = 1
        if hasattr(exception, "exitcode"):
            exitcode = exception.exitcode
        LOG.uncaught(exception)
    LOG.diagnostic(f"Exit code = {exitcode}")


def start_gui() -> int:
    LOG.trace("Starting up the GUI")
    q_app = QApplication([])
    GUI = DemoWindow(q_app)
    GUI.show()
    return q_app.exec_()


def load_config(configfile: Path):
    """
    So far, CONFIG contains the command-line switches.
    Here, we'll add the values of the configuration INI file (if there is one) and/or set various default values.
    """
    LOG.trace("Loading config")
    parser = GWConfigParser(configfile)

    CONFIG.serif_typeface = "Times New Roman"
    CONFIG.sans_typeface = "Arial"
    if parser.has_section("display"):
        CONFIG.serif_typeface = parser["display"].gettext(
            "serif_typeface", CONFIG.serif_typeface
        )
        CONFIG.sans_typeface = parser["display"].gettext(
            "sans_typeface", CONFIG.sans_typeface
        )


def main():
    global LOG
    load_command_line(sys.argv[1:])
    LOG = setup_logging(
        loglevel=CONFIG.loglevel, logfile=CONFIG.logfile, nocolor=CONFIG.nocolor
    )
    LOG.trace("(Previously) Loaded command line and set up logging.")
    # try:
    load_config(configfile=Path(CONFIG.configfile))
    further_initialization()
    x = start_gui()
    finish(exitcode=x)
    # except Exception as e:
    #     finish(exception=e)


if __name__ == "__main__":
    main()