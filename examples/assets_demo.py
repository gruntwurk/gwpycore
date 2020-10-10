from argparse import ArgumentParser
from gwpycore.gw_gui.gw_gui_syntax import SyntaxAssets
from gwpycore import ConfigSettings, GWConfigParser
from typing import Optional
import sys
from pathlib import Path

from gwpycore import (
    QPALETTE_SLUGS,
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


# All icon names must be declared here.
# For icons with alternate states, just name the primary ("off") icon and leave the action name blank here.
# Then, also edit reload_icons() to have it manually load the icon (as an "off"/"on" pair)
ICON_MAP = {
    "about": ("action_about", None, None),
    "bug_report": ("action_report_bug", None, None),
    "calendar": ("action_date", None, None),
    "colors": ("action_font_color", None, None),
    "download_cloud": ("action_updates", None, None),
    "edit_bold": ("action_edit_bold", None, None),
    "edit_copy": ("action_edit_copy", None, None),
    "edit_cut": ("action_edit_cut", None, None),
    "edit_delete": ("", QStyle.SP_DialogDiscardButton, "edit-delete"),
    "edit_italic": ("action_edit_italic", None, None),
    "edit_paste": ("action_edit_paste", None, None),
    "edit_redo": ("action_edit_redo", None, None),
    "edit_underline": ("action_edit_underline", None, None),
    "edit_undo": ("action_edit_undo", None, None),
    "export_pdf": ("action_export_pdf", None, None),
    "file_close": ("action_file_close", QStyle.SP_DialogCloseButton, "window-close"),
    "file_new": ("action_file_new", None, None),
    "file_open": ("action_file_open", QStyle.SP_DirOpenIcon, "folder-open"),
    "file_save": ("action_file_save", QStyle.SP_DialogSaveButton, "document-save"),
    "file_save_as": ("action_file_save_as", None, None),
    "font": ("action_font", None, None),
    "full_screen": ("action_distraction_free", None, None),
    "hashtag": ("action_hashtag", None, None),
    "help": ("action_help", None, None),
    "journal": ("action_new_entry", None, None),
    "newspaper": ("action_publication", None, None),
    "preview": ("action_print_preview", None, None),
    "print": ("action_print", None, None),
    "quit": ("action_quit", None, None),
    "search": ("action_search", None, "edit-find"),
    "search_replace": ("", None, "edit-find-replace"),
    "select_all": ("action_select_all", None, None),
    "time": ("action_time", None, None),
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