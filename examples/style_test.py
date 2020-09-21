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
    QFontDialog,
    qApp,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

import logging
from gwpycore import CoreActions

LOG = logging.getLogger("main")

(DialogSpec, BaseClass) = uic.loadUiType("examples/style_test.ui")


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


class DemoWindow(BaseClass, DialogSpec, CoreActions):
    def __init__(self, parent, config):
        BaseClass.__init__(self)
        DialogSpec.__init__(self)
        CoreActions.__init__(self)
        self.parent = parent
        self.config = config
        self.setupUi(self)
        self.statusBar()

        self.root_asset_path = Path("examples/assets")
        self.icons = IconAssets(
            ICON_MAP,
            asset_path=self.root_asset_path / "icons",
            fallback_theme="noun-black",
            exclude=[],
            parent=self
        )
        self.skins = SkinAssets(asset_path=self.root_asset_path / "skins")
        self.skins.connect_on_change(self.set_icon_color)

        self.reload_icons()

        self.tree1.expandAll()
        self.printing_source_widget = self.textEdit_2
        self.connect_actions()
        self.textEdit_2.currentCharFormatChanged.connect(
            self.current_char_format_changed
        )
        self.textEdit_2.cursorPositionChanged.connect(self.cursor_position_changed)
        self.font_changed(self.textEdit_2.font())
        self.alignment_changed(self.textEdit_2.alignment())
        self.textEdit_2.document().modificationChanged.connect(
            self.action_File_Save.setEnabled
        )
        self.textEdit_2.document().modificationChanged.connect(self.setWindowModified)
        self.textEdit_2.document().undoAvailable.connect(
            self.action_Edit_Undo.setEnabled
        )
        self.textEdit_2.document().redoAvailable.connect(
            self.action_Edit_Redo.setEnabled
        )
        self.setWindowModified(self.textEdit_2.document().isModified())
        self.action_File_Save.setEnabled(self.textEdit_2.document().isModified())
        self.action_Edit_Undo.setEnabled(self.textEdit_2.document().isUndoAvailable())
        self.action_Edit_Redo.setEnabled(self.textEdit_2.document().isRedoAvailable())
        self.action_Edit_Undo.triggered.connect(self.textEdit_2.undo)
        self.action_Edit_Redo.triggered.connect(self.textEdit_2.redo)
        self.action_Edit_Cut.setEnabled(False)
        self.action_Edit_Copy.setEnabled(False)
        self.action_Edit_Cut.triggered.connect(self.textEdit_2.cut)
        self.action_Edit_Copy.triggered.connect(self.textEdit_2.copy)
        self.action_Edit_Paste.triggered.connect(self.textEdit_2.paste)
        self.textEdit_2.copyAvailable.connect(self.action_Edit_Cut.setEnabled)
        self.textEdit_2.copyAvailable.connect(self.action_Edit_Copy.setEnabled)
        QApplication.clipboard().dataChanged.connect(self.clipboard_data_changed)

    def set_icon_color(self, color: QColor):
        if self.icons.is_colorizable:
            self.icons.flush_icons()
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
        self.connect_core_actions()  # about, report bug, exit, help, etc.
        self.action_Edit_Copy.triggered.connect(self.not_implemented)
        self.action_File_Close.triggered.connect(self.not_implemented)
        self.action_Edit_Cut.triggered.connect(self.not_implemented)
        self.action_Date.triggered.connect(self.not_implemented)
        self.action_Search.triggered.connect(self.not_implemented)
        self.action_Font.triggered.connect(self.font_choice)
        self.action_Font_Color.triggered.connect(self.color_picker)
        self.action_Hashtag.triggered.connect(self.not_implemented)
        self.action_File_Open.triggered.connect(self.not_implemented)
        self.action_Edit_Paste.triggered.connect(self.not_implemented)
        self.action_Print.triggered.connect(self.not_implemented)
        self.action_Publication.triggered.connect(self.not_implemented)
        self.action_Edit_Redo.triggered.connect(self.not_implemented)
        self.action_File_Save.triggered.connect(self.not_implemented)
        self.action_File_Save_As.triggered.connect(self.not_implemented)
        self.action_Select_All.triggered.connect(self.not_implemented)
        self.action_Time.triggered.connect(self.not_implemented)
        self.action_Edit_Undo.triggered.connect(self.not_implemented)



    def text_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            self.action_Edit_Bold.isChecked() and QFont.Bold or QFont.Normal
        )
        self.merge_format_on_word_or_selection(fmt)

    def text_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.action_Edit_Underline.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def text_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.action_Edit_Italic.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def text_family(self, family):
        fmt = QTextCharFormat()
        fmt.setFontFamily(family)
        self.merge_format_on_word_or_selection(fmt)

    def text_size(self, pointSize):
        pointSize = float(pointSize)
        if pointSize > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(pointSize)
            self.merge_format_on_word_or_selection(fmt)

    def text_style(self, styleIndex):
        cursor = self.textEdit_2.textCursor()
        if styleIndex:
            styleDict = {
                1: QTextListFormat.ListDisc,
                2: QTextListFormat.ListCircle,
                3: QTextListFormat.ListSquare,
                4: QTextListFormat.ListDecimal,
                5: QTextListFormat.ListLowerAlpha,
                6: QTextListFormat.ListUpperAlpha,
                7: QTextListFormat.ListLowerRoman,
                8: QTextListFormat.ListUpperRoman,
            }

            style = styleDict.get(styleIndex, QTextListFormat.ListDisc)
            cursor.beginEditBlock()
            blockFmt = cursor.blockFormat()
            listFmt = QTextListFormat()

            if cursor.currentList():
                listFmt = cursor.currentList().format()
            else:
                listFmt.setIndent(blockFmt.indent() + 1)
                blockFmt.setIndent(0)
                cursor.setBlockFormat(blockFmt)

            listFmt.setStyle(style)
            cursor.createList(listFmt)
            cursor.endEditBlock()
        else:
            bfmt = QTextBlockFormat()
            bfmt.setObjectIndex(-1)
            cursor.mergeBlockFormat(bfmt)

    def text_color(self):
        col = QColorDialog.getColor(self.textEdit_2.textColor(), self)
        if not col.isValid():
            return

        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self.merge_format_on_word_or_selection(fmt)
        # self.colorChanged(col)

    def text_align(self, action_):
        if action_ == self.action_AlignLeft:
            self.textEdit_2.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif action_ == self.action_AlignCenter:
            self.textEdit_2.setAlignment(Qt.AlignHCenter)
        elif action_ == self.action_AlignRight:
            self.textEdit_2.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif action_ == self.action_AlignJustify:
            self.textEdit_2.setAlignment(Qt.AlignJustify)

    def current_char_format_changed(self, format):
        self.font_changed(format.font())
        # self.colorChanged(format.foreground().color())

    def cursor_position_changed(self):
        self.alignment_changed(self.textEdit_2.alignment())

    def clipboard_data_changed(self):
        pass  # self.action_Edit_Paste.setEnabled(len(QApplication.clipboard().text()) != 0)

    def merge_format_on_word_or_selection(self, format):
        cursor = self.textEdit_2.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.textEdit_2.mergeCurrentCharFormat(format)

    def font_changed(self, font):
        # self.combo_Font.setCurrentIndex(
        #     self.combo_Font.findText(QFontInfo(font).family()))
        # self.combo_Font_Size.setCurrentIndex(
        #     self.combo_Font_Size.findText("%s" % font.pointSize()))
        self.action_Edit_Bold.setChecked(font.bold())
        self.action_Edit_Italic.setChecked(font.italic())
        self.action_Edit_Underline.setChecked(font.underline())

    def alignment_changed(self, alignment):
        if alignment & Qt.AlignLeft:
            self.action_AlignLeft.setChecked(True)
        elif alignment & Qt.AlignHCenter:
            self.action_AlignCenter.setChecked(True)
        elif alignment & Qt.AlignRight:
            self.action_AlignRight.setChecked(True)
        elif alignment & Qt.AlignJustify:
            self.action_AlignJustify.setChecked(True)

    def font_choice(self):
        font, valid = QFontDialog.getFont()
        if valid:
            self.textEdit_2.setFont(font)

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