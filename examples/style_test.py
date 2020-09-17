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
from gwpycore.gw_gui.gw_gui_dialogs import ask_user_to_choose
from gwpycore.gw_gui.gw_gui_skins import SkinAssets
from PyQt5 import uic

from gwpycore import basic_cli_parser

from PyQt5.QtCore import QFileInfo, QSize, QStringListModel, Qt
from PyQt5.QtGui import (
    QTextDocument,
    QFont,
    QIcon,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocumentWriter,
    QTextListFormat,
)
from PyQt5.QtWidgets import (
    QApplication,
    QTreeWidgetItem,
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

import logging
from gwpycore import CoreActions


LOG = logging.getLogger("main")

(DialogSpec, BaseClass) = uic.loadUiType("examples/style_test.ui")


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

        self.skins = SkinAssets(asset_path = self.root_asset_path / "skins")
        self.skin_list = [x for x in self.skins.themes().keys()]
        self.comboSkins.insertItems(0,self.skin_list)
        self.current_skin = -1
        self.next_skin()

        self.tree1.setIconSize(QSize(0, 0))
        # self.tree1.setStyleSheet(
        #     """
        # QTreeView {
        #     padding:0;
        #     margin:0;
        #     alternate-background-color: #f6fafb;
        #     show-decoration-selected: 0;
        # }
        # QTreeView::item {
        #     padding:0;
        #     margin:0;
        #     border: 1px solid #d9d9d9;
        #     border-top-color: transparent;
        #     border-bottom-color: transparent;
        # }
        # QTreeView::item:hover {
        #     border: 1px solid #ffaa00;
        # }
        # QTreeView::item::selected {
        #     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
        #     border: 1px solid #bfcde4;
        # }
        # """
        # )
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
        self.action_AsciiDoc_View.toggled.connect(self.actionTextBold.setEnabled)
        self.action_AsciiDoc_View.toggled.connect(self.actionTextItalic.setEnabled)
        self.action_AsciiDoc_View.toggled.connect(self.actionTextUnderline.setEnabled)
        QApplication.clipboard().dataChanged.connect(self.clipboardDataChanged)
        self.buttonPreviousSkin.released.connect(self.previous_skin)
        self.buttonNextSkin.released.connect(self.next_skin)

        if self.config.devmode:
            self.populate_tree_view()

    def next_skin(self):
        self.current_skin += 1
        if self.current_skin >= len(self.skin_list):
            self.current_skin = 0
        self.comboSkins.setCurrentIndex(self.current_skin)
        self.skins.set_theme(self.skin_list[self.current_skin])
        self.skins.apply_theme()

    def previous_skin(self):
        self.current_skin -= 1
        if self.current_skin < 0:
            self.current_skin = len(self.skin_list)-1
        self.comboSkins.setCurrentIndex(self.current_skin)
        self.skins.set_theme(self.skin_list[self.current_skin])
        self.skins.apply_theme()

    def file_open(self):
        LOG.trace("Enter: file_open")
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            directory=str(self.config.work_dir),
            filter="AsciiDoc-Files (*.adoc *.asciidoc);;HTML-Files (*.htm *.html);;All Files (*)",
        )

        self.work_segment.load_file(path)
        self.populate_tree_view()

    def populate_tree_view(self):
        self.tree1.setColumnCount(1)
        items = []
        for i in range(10):
            items.append(QTreeWidgetItem(None, QStringListModel(f"item: {i}")))
        self.tree1.insertTopLevelItems(None, items)
        self.tree1.expandAll()


    def file_save(self):
        pass

    def connect_actions(self):
        self.connect_core_actions()
        self.action_Analyze.triggered.connect(self.not_implemented)
        self.action_AsciiDoc_View.triggered.connect(self.not_implemented)
        self.action_Copy.triggered.connect(self.not_implemented)
        self.action_Close.triggered.connect(self.not_implemented)
        self.action_Cut.triggered.connect(self.not_implemented)
        self.action_Date.triggered.connect(self.not_implemented)
        self.action_Find.triggered.connect(self.not_implemented)
        self.action_Fixup.triggered.connect(self.not_implemented)
        self.action_Font.triggered.connect(self.font_choice)
        self.action_Font_Color.triggered.connect(self.color_picker)
        self.action_Hashtag.triggered.connect(self.not_implemented)
        self.action_Open.triggered.connect(self.file_open)
        self.action_Paste.triggered.connect(self.not_implemented)
        self.action_Print.triggered.connect(self.not_implemented)
        self.action_Print_Preview.triggered.connect(self.print_preview)
        self.action_Publication.triggered.connect(self.not_implemented)
        self.action_Redo.triggered.connect(self.not_implemented)
        self.action_Save.triggered.connect(self.file_save)
        self.action_Save_As.triggered.connect(self.not_implemented)
        self.action_Select_All.triggered.connect(self.not_implemented)
        self.action_Time.triggered.connect(self.not_implemented)
        self.action_Undo.triggered.connect(self.not_implemented)
        self.action_Wrap_Text.triggered.connect(self.not_implemented)
        self.tree1.activated.connect(self.show_entry)

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.show_preview)
        preview.exec_()

    def show_preview(self, printer):
        self.textEdit_2.print_(printer)

    def filePrintPdf(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", None, "PDF files (*.pdf);;All Files (*)"
        )

        if fn:
            if QFileInfo(fn).suffix().isEmpty():
                fn += ".pdf"

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.textEdit_2.document().print_(printer)

    def textBold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            self.actionTextBold.isChecked() and QFont.Bold or QFont.Normal
        )
        self.mergeFormatOnWordOrSelection(fmt)

    def textUnderline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.actionTextUnderline.isChecked())
        self.mergeFormatOnWordOrSelection(fmt)

    def textItalic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.actionTextItalic.isChecked())
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

    def textAlign(self, action):
        if action == self.actionAlignLeft:
            self.textEdit_2.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif action == self.actionAlignCenter:
            self.textEdit_2.setAlignment(Qt.AlignHCenter)
        elif action == self.actionAlignRight:
            self.textEdit_2.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif action == self.actionAlignJustify:
            self.textEdit_2.setAlignment(Qt.AlignJustify)

    def currentCharFormatChanged(self, format):
        self.fontChanged(format.font())
        # self.colorChanged(format.foreground().color())

    def cursorPositionChanged(self):
        self.alignmentChanged(self.textEdit_2.alignment())

    def clipboardDataChanged(self):
        pass  # self.actionPaste.setEnabled(len(QApplication.clipboard().text()) != 0)

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
        self.actionTextBold.setChecked(font.bold())
        self.actionTextItalic.setChecked(font.italic())
        self.actionTextUnderline.setChecked(font.underline())

    def alignmentChanged(self, alignment):
        if alignment & Qt.AlignLeft:
            self.actionAlignLeft.setChecked(True)
        elif alignment & Qt.AlignHCenter:
            self.actionAlignCenter.setChecked(True)
        elif alignment & Qt.AlignRight:
            self.actionAlignRight.setChecked(True)
        elif alignment & Qt.AlignJustify:
            self.actionAlignJustify.setChecked(True)

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