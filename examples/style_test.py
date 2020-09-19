from argparse import ArgumentParser, Namespace
from typing import Optional
import sys
from pathlib import Path

from gwpycore.gw_basis.gw_config import parse_config
from gwpycore.gw_basis.gw_logging import setup_logging
from gwpycore.gw_gui.gw_gui_images import ImageAssets
from gwpycore.gw_gui.gw_gui_fonts import FontAssets
from gwpycore.gw_gui.gw_gui_syntax import SyntaxHighlightAssets
from gwpycore.gw_gui.gw_gui_icons import IconAssets
from gwpycore.gw_gui.gw_gui_dialogs import ICON_WARNING, ask_user_to_choose
from gwpycore.gw_gui.gw_gui_skins import SkinAssets
from gwpycore.gw_gui.gw_gui_icons import IconAssets
from PyQt5 import uic

from gwpycore import basic_cli_parser

from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import (
    QColor, QPalette,
    QFont,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextListFormat,
)
from PyQt5.QtWidgets import (
    QApplication,
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog, qApp,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

import logging
from gwpycore import CoreActions


LOG = logging.getLogger("main")

(DialogSpec, BaseClass) = uic.loadUiType("examples/style_test.ui")

QPALETTE_SLUGS = ["default", "window", "shadow", "base", "dark", "tooltipbase", "highlight", "mid", "alternatebase", "button", "tooltiptext", "placeholdertext", "midlight", "windowtext", "light", "text", "brighttext", "buttontext", "highlightedtext", "link", "linkvisited"]

ICON_MAP = {
    "about": (None,None),
    "adobe": (None,None),
    "bug_report": (None,None),
    "calendar": (None,None),
    "close": (None,None),
    "colors": (None,None),
    "download_cloud": (None,None),
    "edit_bold": (None,None),
    "edit_copy": (None,None),
    "edit_cut": (None,None),
    "edit_underline": (None,None),
    "edit_italic": (None,None),
    "edit_paste": (None,None),
    "edit_redo": (None,None),
    "edit_undo": (None,None),
    "find": (None,None),
    "font": (None,None),
    "full_screen": (None,None),
    "hashtag": (None,None),
    "help": (None,None),
    "newspaper": (None,None),
    "open": (None,None),
    "preview": (None,None),
    "print": (None,None),
    "quit": (None,None),
    "save": (None,None),
    "save_as": (None,None),
    "select_all": (None,None),
    "time": (None,None),
    "word_wrap": (None,None)}


POINT_OUT_COLOR = QColor("#FF0000")


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
        self.icons = IconAssets(ICON_MAP, asset_path = self.root_asset_path / "icons", fallback_theme="noun-black", exclude=[])
        self.skins = SkinAssets(asset_path = self.root_asset_path / "skins")
        self.skins.connect_on_change(self.set_icon_color)

        self.setup_icons()

        self.tree1.expandAll()

        self.connect_actions()
        self.textEdit_2.currentCharFormatChanged.connect(self.currentCharFormatChanged)
        self.textEdit_2.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.fontChanged(self.textEdit_2.font())
        self.alignmentChanged(self.textEdit_2.alignment())
        self.textEdit_2.document().modificationChanged.connect(
            self.action_Save.setEnabled
        )
        self.textEdit_2.document().modificationChanged.connect(self.setWindowModified)
        self.textEdit_2.document().undoAvailable.connect(self.action_Undo.setEnabled)
        self.textEdit_2.document().redoAvailable.connect(self.action_Redo.setEnabled)
        self.setWindowModified(self.textEdit_2.document().isModified())
        self.action_Save.setEnabled(self.textEdit_2.document().isModified())
        self.action_Undo.setEnabled(self.textEdit_2.document().isUndoAvailable())
        self.action_Redo.setEnabled(self.textEdit_2.document().isRedoAvailable())
        self.action_Undo.triggered.connect(self.textEdit_2.undo)
        self.action_Redo.triggered.connect(self.textEdit_2.redo)
        self.action_Cut.setEnabled(False)
        self.action_Copy.setEnabled(False)
        self.action_Cut.triggered.connect(self.textEdit_2.cut)
        self.action_Copy.triggered.connect(self.textEdit_2.copy)
        self.action_Paste.triggered.connect(self.textEdit_2.paste)
        self.textEdit_2.copyAvailable.connect(self.action_Cut.setEnabled)
        self.textEdit_2.copyAvailable.connect(self.action_Copy.setEnabled)
        QApplication.clipboard().dataChanged.connect(self.clipboardDataChanged)
        self.action_Cycle_Skin.triggered.connect(self.skins.next_skin)
        self.action_Previous_Skin.triggered.connect(self.skins.previous_skin)

    def set_icon_color(self, color: QColor):
        if self.icons.is_colorizable:
            self.icons.flush_icons()
            self.icons.colorize(color)
            self.setup_icons()

    def setup_icons(self):
        self.action_About.setIcon(self.icons.get_icon("about"))
        self.action_Bug.setIcon(self.icons.get_icon("bug_report"))
        self.action_Close.setIcon(self.icons.get_icon("close"))
        self.action_Copy.setIcon(self.icons.get_icon("edit_copy"))
        self.action_Cut.setIcon(self.icons.get_icon("edit_cut"))
        self.action_Date.setIcon(self.icons.get_icon("calendar"))
        self.action_Distraction_Free.setIcon(self.icons.get_icon("full_screen"))
        self.action_Exit.setIcon(self.icons.get_icon("quit"))
        self.action_Find.setIcon(self.icons.get_icon("find"))
        self.action_Font.setIcon(self.icons.get_icon("font"))
        self.action_Font_Color.setIcon(self.icons.get_icon("colors"))
        self.action_Hashtag.setIcon(self.icons.get_icon("hashtag"))
        self.action_Help.setIcon(self.icons.get_icon("help"))
        self.action_Open.setIcon(self.icons.get_icon("open"))
        self.action_Paste.setIcon(self.icons.get_icon("edit_paste"))
        self.action_Print.setIcon(self.icons.get_icon("print"))
        self.action_Print_Preview.setIcon(self.icons.get_icon("preview"))
        self.action_PrintPdf.setIcon(self.icons.get_icon("adobe"))
        self.action_Publication.setIcon(self.icons.get_icon("newspaper"))
        self.action_Redo.setIcon(self.icons.get_icon("edit_redo"))
        self.action_Save.setIcon(self.icons.get_icon("save"))
        self.action_Save_As.setIcon(self.icons.get_icon("save_as"))
        self.action_Select_All.setIcon(self.icons.get_icon("select_all"))
        self.action_TextBold.setIcon(self.icons.get_icon("edit_bold"))
        self.action_TextItalic.setIcon(self.icons.get_icon("edit_italic"))
        self.action_TextUnderline.setIcon(self.icons.get_icon("edit_underline"))
        self.action_Time.setIcon(self.icons.get_icon("time"))
        self.action_Undo.setIcon(self.icons.get_icon("edit_undo"))
        self.action_Updates.setIcon(self.icons.get_icon("download_cloud"))
        self.action_Word_Wrap.setIcon(self.icons.get_icon("word_wrap"))

    def connect_actions(self):
        self.connect_core_actions() # about, report bug, exit, help, etc.
        self.action_Font.triggered.connect(self.font_choice)
        self.action_Font_Color.triggered.connect(self.color_picker)
        self.action_Print_Preview.triggered.connect(self.print_preview)
        self.action_Copy.triggered.connect(self.not_implemented)
        self.action_Close.triggered.connect(self.not_implemented)
        self.action_Cut.triggered.connect(self.not_implemented)
        self.action_Date.triggered.connect(self.not_implemented)
        self.action_Find.triggered.connect(self.not_implemented)
        self.action_Hashtag.triggered.connect(self.not_implemented)
        self.action_Open.triggered.connect(self.not_implemented)
        self.action_Paste.triggered.connect(self.not_implemented)
        self.action_Print.triggered.connect(self.not_implemented)
        self.action_Publication.triggered.connect(self.not_implemented)
        self.action_Redo.triggered.connect(self.not_implemented)
        self.action_Save.triggered.connect(self.not_implemented)
        self.action_Save_As.triggered.connect(self.not_implemented)
        self.action_Select_All.triggered.connect(self.not_implemented)
        self.action_Time.triggered.connect(self.not_implemented)
        self.action_Undo.triggered.connect(self.not_implemented)
        self.action_Word_Wrap.triggered.connect(self.not_implemented)

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.show_preview)
        preview.exec_()

    def show_preview(self, printer):
        self.textEdit_2.print_(printer)

    def filePrintPdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", None, "PDF files (*.pdf);;All Files (*)"
        )

        if filename:
            if QFileInfo(filename).suffix().isEmpty():
                filename += ".pdf"

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            self.textEdit_2.document().print_(printer)

    def textBold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            self.action_TextBold.isChecked() and QFont.Bold or QFont.Normal
        )
        self.mergeFormatOnWordOrSelection(fmt)

    def textUnderline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.action_TextUnderline.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textItalic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.action_TextItalic.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textFamily(self, family):
        fmt = QTextCharFormat()
        fmt.setFontFamily(family)
        self.mergeFormatOnWordOrSelection(fmt)

    def textSize(self, pointSize):
        pointSize = float(pointSize)
        if pointSize > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(pointSize)
            self.mergeFormatOnWordOrSelection(fmt)

    def textStyle(self, styleIndex):
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

    def textColor(self):
        col = QColorDialog.getColor(self.textEdit_2.textColor(), self)
        if not col.isValid():
            return

        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self.mergeFormatOnWordOrSelection(fmt)
        # self.colorChanged(col)

    def textAlign(self, action_):
        if action_ == self.action_AlignLeft:
            self.textEdit_2.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif action_ == self.action_AlignCenter:
            self.textEdit_2.setAlignment(Qt.AlignHCenter)
        elif action_ == self.action_AlignRight:
            self.textEdit_2.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif action_ == self.action_AlignJustify:
            self.textEdit_2.setAlignment(Qt.AlignJustify)

    def currentCharFormatChanged(self, format):
        self.fontChanged(format.font())
        # self.colorChanged(format.foreground().color())

    def cursorPositionChanged(self):
        self.alignmentChanged(self.textEdit_2.alignment())

    def clipboardDataChanged(self):
        pass  # self.action_Paste.setEnabled(len(QApplication.clipboard().text()) != 0)

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.textEdit_2.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.textEdit_2.mergeCurrentCharFormat(format)

    def fontChanged(self, font):
        # self.combo_Font.setCurrentIndex(
        #     self.combo_Font.findText(QFontInfo(font).family()))
        # self.combo_Font_Size.setCurrentIndex(
        #     self.combo_Font_Size.findText("%s" % font.pointSize()))
        self.action_TextBold.setChecked(font.bold())
        self.action_TextItalic.setChecked(font.italic())
        self.action_TextUnderline.setChecked(font.underline())

    def alignmentChanged(self, alignment):
        if alignment & Qt.AlignLeft:
            self.action_AlignLeft.setChecked(True)
        elif alignment & Qt.AlignHCenter:
            self.action_AlignCenter.setChecked(True)
        elif alignment & Qt.AlignRight:
            self.action_AlignRight.setChecked(True)
        elif alignment & Qt.AlignJustify:
            self.action_AlignJustify.setChecked(True)

    def color_picker(self):
        # self.textEdit_2.selectAll()
        self.textEdit_2.setTextColor(QColorDialog.getColor())

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
    CONFIG.application_title ="Asset Management Demonstration"
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
    CONFIG = load_config(
        configfile=Path(switches.configfile), initial_config=switches
    )
    further_initialization()
    x = start_gui(CONFIG)
    finish(exitcode=x)
    # except Exception as e:
    #     finish(exception=e)


if __name__ == "__main__":
    main()