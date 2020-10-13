from abc import abstractmethod
from gwpycore.gw_basis.gw_exceptions import GruntWurkUserEscape
from gwpycore.gw_basis.gw_config import ConfigSettings
from pathlib import Path
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QTextCursor,
    QTextDocument,
    QTextDocumentWriter,
)
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QMenuBar,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
)
from gwpycore.gw_gui.gw_gui_dialogs import (
    InspectionDialog,
    ask_user_to_confirm,
    inform_user,
    show_information,
)
import webbrowser
from gwpycore import ICON_WARNING

import logging

LOG = logging.getLogger("main")

CONFIG = ConfigSettings()


class GWStandardApp:
    """
    This is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        action_about
        action_report_bug
        action_quit
        action_help
        action_updates
        action_inspect_config
        action_distraction_free
        action_cycle_skin and action_previous_skin
    """

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

    def set_asset_root(self, root: str):
        self.root_asset_path = Path(root)

    def asset_root(self) -> Path:
        return self.root_asset_path

    def keep_actions_active(self):
        """
        If a the menu bar is rendered invisble, then all of the actions will be inaccessible, unless...
        * The action is also associated with another widget (e.g. a toolbar) that is still visible, or
        * The action is directly added to the window (widget) -- which is what we're doing here.
        """
        if menubar := self.findChild(QMenuBar):
            all_actions = menubar.findChildren(QAction)
            for action in all_actions:
                self.addAction(action)

    def not_implemented(self):
        inform_user(
            "Sorry, this feature is curently not available.",
            ICON_WARNING,
            parent=self,
            title="Not Implemented",
        )

    def standard_close_application(self):
        if not CONFIG.confirm_exit:
            self.close()
        if ask_user_to_confirm("Exit, are you sure?", parent=self):
            self.close()
        # FIXME closes anyway

    def standard_about(self):
        if hasattr(CONFIG, "application_title"):
            info = f"{CONFIG.application_title}\nVersion: {CONFIG.version}"
            inform_user(info, parent=self, title="About")

    def standard_report_bug(self):
        if hasattr(CONFIG, "report_bug_url"):
            webbrowser.open(CONFIG.report_bug_url, new=2)
        else:
            self.not_implemented()

    def standard_show_help(self):
        help_text_path = self.asset_root() / "help/help.html"
        if help_text_path.exists():
            with help_text_path.open("r") as f:
                show_information(f.read(), parent=self)
        elif hasattr(CONFIG, "documentation_url"):
            webbrowser.open(CONFIG.documentation_url, new=2)
        else:
            self.not_implemented()

    def standard_check_for_updates(self):
        if hasattr(CONFIG, "latest_release_url"):
            # FIXME Scrape the version number from self.latest_release_url
            self.not_implemented()
        else:
            self.not_implemented()

    def standard_distraction_free(self):
        screen_no = QApplication.desktop().screenNumber(self)
        full_screen = QApplication.desktop().availableGeometry(screen_no)
        if hasattr(self, "original_geometry") and (self.geometry() == full_screen):
            self.setGeometry(self.original_geometry)
        else:
            self.original_geometry = self.geometry()
            self.setGeometry(full_screen)
        self.show()

    def standard_hide_menu(self):
        if menubar := self.findChild(QMenuBar):
            menubar.setVisible(not menubar.isVisible())

    def standard_inspect_config(self):
        keys = CONFIG.sorted_keys()
        inspector = InspectionDialog(
            prompt="The current configuration is:",
            title="Diagnostic: Configuration Settings",
            rows=len(keys),
            cols=2,
        )
        for i, key in enumerate(keys):
            value = CONFIG.get(key)
            inspector.info.setItem(i, 0, QTableWidgetItem(key))
            inspector.info.setItem(i, 1, QTableWidgetItem(value.__repr__()))
        inspector.exec_()

    def connect_standard_actions(self):
        self.connect_action("action_about")
        self.connect_action("action_help", self.standard_show_help)
        self.connect_action("action_report_bug")
        self.connect_action("action_quit", self.standard_close_application)
        self.connect_action("action_updates", self.standard_check_for_updates)
        self.connect_action("action_inspect_config")
        self.connect_action("action_distraction_free")
        self.connect_action("action_hide_menu")
        if hasattr(self, "skins"):
            self.connect_action("action_cycle_skin", self.skins.next_skin)
            self.connect_action("action_previous_skin", self.skins.previous_skin)
            self.connect_action("action_inspect_skin", self.skins.inspect_skin)

    def connect_action(self, action_name: str, method=None) -> bool:
        """
        If the method isn't specified, we assume self.standard_xxx goes with action_xxx
        """
        if not hasattr(self, action_name):
            return False
        if not method:
            method_name = action_name.replace("action_", "standard_",1)
            if hasattr(self, method_name):
                method = getattr(self, method_name)
        if method:
            self.__dict__[action_name].triggered.connect(method)
        return True

    def disconnect_all(self, signal):
        while True:
            try:
                signal.disconnect()
            except TypeError:
                break


class GWStandardEditorApp(GWStandardApp):
    """
    This variation of GWStandardApp adds standard text-edit handling.
    As with GWStandardApp, this is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        * (All of the actions handled by GWStandardApp), plus:
        * action_file_open, action_file_save, action_file_save_as
        * action_print_preview, action_export_pdf
        * action_edit_cut, action_edit_copy, action_edit_paste
        * action_font, action_font_color
        * action_edit_undo, action_edit_redo
        * action_cycle_syntax_scheme, action_previous_syntax_scheme
    """

    def __init__(self, **kwds) -> None:
        self.edit_control: QTextEdit = None
        self.current_color = QColor()
        self.current_font = QFont()
        super().__init__(**kwds)

    def standard_font_choice(self):
        new_font, valid = QFontDialog.getFont()
        if not valid:
            return
        self.current_font = new_font
        self.edit_control.setFont(new_font)
        if self.callback_font_choice:
            self.callback_font_choice(new_font)

    def standard_color_picker(self):
        new_color = QColorDialog.getColor(initial=self.current_color, parent=self)
        if not new_color.isValid():
            return
        self.current_color = new_color
        self.edit_control.setTextColor(new_color)
        if self.callback_color_choice:
            self.callback_color_choice(new_color)

    def standard_file_open(self):
        """
        Invokes the system's file-open dialog in the CONFIG.working_dir folder, with a filter per CONFIG.file_open_filter (or all files if not defined).
        If CONFIG.file_open_callback is defined, then that function is invoked to actually load the file; otherwise, a standard method will handle loading
        self.edit_control with either plain text or HTML.
        """
        callback = self.callback_file_open
        if not callback:
            callback = self.standard_load_file

        dir = str(CONFIG.working_dir)

        filter = CONFIG.file_open_filter
        if not filter:
            filter = "All Files (*)"

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            directory=dir,
            filter=filter,
        )
        callback(path)

    def standard_load_file(self, path_str: str):
        """
        This is the dafault callback method for standard_file_open, when CONFIG.file_open_callback is not defined.
        """
        source = Path(path_str)
        doc: QTextDocument = self.edit_control.document()
        with source.open("rt") as f:
            if source.suffix().lower() in [".html", ".htm"]:
                doc.setHtml(f.read())
            else:
                doc.setPlainText(f.read())

    def standard_file_new(self):
        if self.is_clean():
            self.edit_control.clear()

    def standard_file_save(self):
        if self.current_file_path:
            self.do_file_save()
        else:
            self.file_save_as()

    def standard_file_save_as(self):
        filter = CONFIG.file_save_filter
        if not filter:
            filter = "ODF files (*.odt);;HTML-Files (*.htm *.html);;All Files (*)"

        name, _ = QFileDialog.getSaveFileName(self, "Save as...", None, filter)
        if not name:
            return False
        self.current_file_path = Path(name)
        self.do_file_save()

    def do_file_save(self):
        # FIXME What about plain text? Also, ODT, really?
        if self.current_file_path.suffix().lower() not in [".odt", ".htm", ".html"]:
            self.current_file_path = self.current_file_path / ".odt"
        writer = QTextDocumentWriter(str(self.current_file_path))
        success = writer.write(self.edit_control.document())
        if success:
            self.edit_control.document().setModified(False)
        return success

    def standard_print_preview(self):
        if not self.edit_control:
            return
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.show_preview)
        preview.exec_()

    def standard_export_pdf(self):
        if not self.edit_control:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", None, "PDF files (*.pdf);;All Files (*)"
        )
        if filename:
            if QFileInfo(filename).suffix().isEmpty():
                filename += ".pdf"
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            self.edit_control.document().print_(printer)

    def show_preview(self, printer):
        self.edit_control.print_(printer)

    def cursor_with_word_selected(self) -> QTextCursor:
        cursor: QTextCursor = self.edit_control.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        return cursor

    def standard_clipboard_data_changed(self):
        if hasattr(self, "action_edit_paste"):
            self.action_edit_paste.setEnabled(len(QApplication.clipboard().text()) != 0)

    def closeEvent(self, e):
        if self.is_clean():
            e.accept()
        else:
            e.ignore()

    def is_clean(self):
        if not self.edit_control.document().isModified():
            return True
        try:
            if ask_user_to_confirm(
                "The document has been modified.\nDo you want to save your changes?",
                parent=self,
                icon=ICON_WARNING,
                title="Application",
            ):
                return self.callback_file_save()
        except GruntWurkUserEscape as e:
            return False
        return True

    def connect_standard_actions(self):
        super().connect_standard_actions()
        ec = self.edit_control

        # If the method isn't specified, it assumes self.standard_xxx goes with action_xxx
        self.connect_action("action_export_pdf")
        self.connect_action("action_file_open")
        if self.connect_action("action_file_save"):
            ec.document().modificationChanged.connect(self.action_file_save.setEnabled)
        self.connect_action("action_file_save_as")
        self.connect_action("action_print_preview")
        if hasattr(self, "syntax_schemes"):
            self.connect_action(
                "action_cycle_syntax_scheme", self.syntax_schemes.next_syntax_scheme
            )
            self.connect_action(
                "action_previous_syntax_scheme",
                self.syntax_schemes.previous_syntax_scheme,
            )
        if self.connect_action("action_edit_copy", ec.copy):
            ec.copyAvailable.connect(self.action_edit_copy.setEnabled)
        if self.connect_action("action_edit_cut", ec.cut):
            ec.copyAvailable.connect(self.action_edit_cut.setEnabled)
        self.connect_action("action_edit_paste", ec.paste)
        if self.connect_action("action_edit_undo", ec.undo):
            ec.document().undoAvailable.connect(self.action_edit_undo.setEnabled)
        if self.connect_action("action_edit_redo", ec.redo):
            ec.document().redoAvailable.connect(self.action_edit_redo.setEnabled)
        self.connect_action("action_font", self.standard_font_choice)
        self.connect_action("action_font_color", self.standard_color_picker)

        QApplication.clipboard().dataChanged.connect(
            self.standard_clipboard_data_changed
        )
        ec.document().modificationChanged.connect(self.setWindowModified)

    def initialize_editing(self):
        ec = self.edit_control
        if hasattr(self, "action_file_save"):
            self.action_file_save.setEnabled(ec.document().isModified())
        if hasattr(self, "action_edit_undo"):
            self.action_edit_undo.setEnabled(ec.document().isUndoAvailable())
        if hasattr(self, "action_edit_redo"):
            self.action_edit_redo.setEnabled(ec.document().isRedoAvailable())
        if hasattr(self, "action_edit_cut"):
            self.action_edit_cut.setEnabled(False)
        if hasattr(self, "action_edit_copy"):
            self.action_edit_copy.setEnabled(False)
        if hasattr(self, "font_changed"):
            self.font_changed(ec.font())
        if hasattr(self, "color_changed"):
            self.color_changed(ec.textColor())
        self.setWindowModified(ec.document().isModified())

    def add_font_widgets(self, toolbar: QToolBar):
        self.combo_Paragraph = QComboBox(toolbar)
        toolbar.addWidget(self.combo_Paragraph)
        self.combo_Paragraph.addItem("Paragraph")
        self.combo_Paragraph.addItem("Bullet List (Disc)")
        self.combo_Paragraph.addItem("Bullet List (Circle)")
        self.combo_Paragraph.addItem("Bullet List (Square)")
        self.combo_Paragraph.addItem("Ordered List (Decimal)")
        self.combo_Paragraph.addItem("Ordered List (Alpha lower)")
        self.combo_Paragraph.addItem("Ordered List (Alpha upper)")
        self.combo_Paragraph.addItem("Ordered List (Roman lower)")
        self.combo_Paragraph.addItem("Ordered List (Roman upper)")
        self.combo_Paragraph.activated.connect(self.textStyle)

        self.combo_Font = QFontComboBox(toolbar)
        toolbar.addWidget(self.combo_Font)
        self.combo_Font.activated[str].connect(self.textFamily)

        self.combo_Font_Size = QComboBox(toolbar)
        self.combo_Font_Size.setObjectName("combo_Font_Size")
        toolbar.addWidget(self.combo_Font_Size)
        self.combo_Font_Size.setEditable(True)
        db = QFontDatabase()
        for size in db.standardSizes():
            self.combo_Font_Size.addItem(f"{size}")
        self.combo_Font_Size.activated[str].connect(self.textSize)
        self.combo_Font_Size.setCurrentIndex(
            self.combo_Font_Size.findText(f"{QApplication.font().pointSize()}")
        )


__all__ = ("GWStandardApp", "GWStandardEditorApp")
