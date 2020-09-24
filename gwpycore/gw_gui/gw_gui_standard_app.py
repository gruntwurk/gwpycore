from pathlib import Path
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QTextCursor, QTextDocumentWriter
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtWidgets import QApplication, QColorDialog, QComboBox, QFileDialog, QFontComboBox, QFontDialog, QTextEdit, QToolBar
from gwpycore.gw_gui.gw_gui_dialogs import ask_user_to_confirm, inform_user
import webbrowser
from gwpycore import ICON_WARNING

class GWStandardApp():
    """
    This is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        action_About
        action_Report_Bug
        action_Quit
        action_Help
        action_Updates
        action_Inspect_Config
        action_Distraction_Free
        action_Cycle_Skin and action_Previous_Skin
    """
    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

    def not_implemented(self):
        inform_user(
            "Sorry, this feature is curently not available.",
            ICON_WARNING,
            parent=self,
            title="Not Implemented",
        )

    def standard_close_application(self):
        if not self.config.confirm_exit:
            self.close()
        if ask_user_to_confirm("Exit, are you sure?", parent=self):
            self.close()
        # FIXME closes anyway

    def standard_about(self):
        if hasattr(self.config, "application_title"):
            info = f"{self.config.application_title}\nVersion: {self.config.version}"
            inform_user(info, parent=self, title="About")

    def standard_report_bug(self):
        if hasattr(self.config, "report_bug_url"):
            webbrowser.open(self.config.report_bug_url, new=2)
        else:
            self.not_implemented()

    def standard_home_page(self):
        if hasattr(self.config, "documentation_url"):
            webbrowser.open(self.config.documentation_url, new=2)
        else:
            self.not_implemented()

    def standard_check_for_updates(self):
        if hasattr(self.config, "latest_release_url"):
            # FIXME Scrape the version number from self.latest_release_url
            self.not_implemented()
        else:
            self.not_implemented()

    def standard_full_screen(self):
        # FIXME full_screen
        self.not_implemented()

    def standard_inspect_config(self):
        info = []
        for key, value in vars(self.config).items():
            info.append(f"{key} \t= {value.__repr__()}")
        info.sort()
        inform_user(
            "\n".join(info), parent=self, title="Diagnostic: Configuration Settings"
        )

    def connect_standard_actions(self):
        if hasattr(self, "action_About"):
            self.action_About.triggered.connect(self.standard_about)
        if hasattr(self, "action_Report_Bug"):
            self.action_Report_Bug.triggered.connect(self.standard_report_bug)
        if hasattr(self, "action_Quit"):
            self.action_Quit.triggered.connect(self.standard_close_application)
        if hasattr(self, "action_Help"):
            self.action_Help.triggered.connect(self.standard_home_page)
        if hasattr(self, "action_Updates"):
            self.action_Updates.triggered.connect(self.standard_check_for_updates)
        if hasattr(self, "action_Inspect_Config"):
            self.action_Inspect_Config.triggered.connect(self.standard_inspect_config)
        if hasattr(self, "action_Distraction_Free"):
            self.action_Distraction_Free.triggered.connect(self.standard_full_screen)
        if hasattr(self, "action_Cycle_Skin"):
            self.action_Cycle_Skin.triggered.connect(self.skins.next_skin)
        if hasattr(self, "action_Previous_Skin"):
            self.action_Previous_Skin.triggered.connect(self.skins.previous_skin)


class GWStandardEditorApp(GWStandardApp):
    """
    This is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        All of the actions handled by GWStandardApp, plus:
        action_Cycle_Syntax_scheme and action_Previous_Syntax_scheme
        action_Print_Preview and action_Export_Pdf
    """

    def __init__(self, **kwds) -> None:
        self.edit_control: QTextEdit = None
        self.current_color = QColor()
        self.current_font = QFont()
        super().__init__(**kwds)


    def standard_font_choice(self, callback = None):
        new_font, valid = QFontDialog.getFont()
        if not valid:
            return
        self.current_font = new_font
        self.edit_control.setFont(new_font)
        if callback:
            callback(new_font)

    def standard_color_picker(self, callback = None):
        new_color = QColorDialog.getColor(initial=self.current_color, parent=self)
        if not new_color.isValid():
            return
        self.current_color = new_color
        self.edit_control.setTextColor(new_color)
        if callback:
            callback(new_color)


    def standard_file_open(self, dir="", filter="All Files (*)", callback=None):
        if not callback:
            callback = self.load_file
        if not dir:
            dir = str(self.config.working_dir)
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            directory=dir,
            filter=filter,
        )
        callback(path)

    def standard_file_new(self):
        if self.is_clean_or_dirty_okay():
            self.edit_control.clear()

    def standard_file_save(self):
        if self.current_file_path:
            self.do_file_save()
        else:
            self.file_save_as()

    def standard_file_save_as(
        self, filter="ODF files (*.odt);;HTML-Files (*.htm *.html);;All Files (*)"
    ):
        name, _ = QFileDialog.getSaveFileName(self, "Save as...", None, filter)
        if not name:
            return False
        self.current_file_path = Path(name)
        self.do_file_save()

    def do_file_save(self):
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
        if hasattr(self, "action_Edit_Paste"):
            self.action_Edit_Paste.setEnabled(len(QApplication.clipboard().text()) != 0)


    def closeEvent(self, e):
        if self.is_clean_or_dirty_okay():
            e.accept()
        else:
            e.ignore()

    def is_clean_or_dirty_okay(self):
        if not self.edit_control.document().isModified():
            return True
        if ask_user_to_confirm(
            "The document has been modified.\nDo you want to save your changes?",
            parent=self,
            icon=ICON_WARNING,
            title="Application",
        ):
            return self.fileSave()
        return True


    def connect_standard_actions(self):
        super().connect_standard_actions()

        if hasattr(self, "action_Export_Pdf"):
            self.action_Export_Pdf.triggered.connect(self.standard_export_pdf)
        if hasattr(self, "action_File_Save"):
            self.action_File_Save.triggered.connect(self.standard_file_save)
            self.edit_control.document().modificationChanged.connect(
                self.action_File_Save.setEnabled
            )
        if hasattr(self, "action_File_Save_As"):
            self.action_File_Save_As.triggered.connect(self.standard_file_save_as)
        if hasattr(self, "action_Print_Preview"):
            self.action_Print_Preview.triggered.connect(self.standard_print_preview)
        if hasattr(self, "action_Cycle_Syntax_scheme"):
            self.action_Cycle_Syntax_scheme.triggered.connect(
                self.syntax_schemes.next_syntax_scheme
            )
        if hasattr(self, "action_Previous_Syntax_scheme"):
            self.action_Previous_Syntax_scheme.triggered.connect(
                self.syntax_schemes.previous_syntax_scheme
            )
        if hasattr(self, "action_Edit_Copy"):
            self.action_Edit_Copy.triggered.connect(self.edit_control.copy)
            self.edit_control.copyAvailable.connect(self.action_Edit_Copy.setEnabled)
        if hasattr(self, "action_Edit_Cut"):
            self.action_Edit_Cut.triggered.connect(self.edit_control.cut)
            self.edit_control.copyAvailable.connect(self.action_Edit_Cut.setEnabled)
        if hasattr(self, "action_Edit_Paste"):
            self.action_Edit_Paste.triggered.connect(self.edit_control.paste)
        if hasattr(self, "action_Edit_Undo"):
            self.action_Edit_Undo.triggered.connect(self.edit_control.undo)
            self.edit_control.document().undoAvailable.connect(
                self.action_Edit_Undo.setEnabled
            )
        if hasattr(self, "action_Edit_Redo"):
            self.action_Edit_Redo.triggered.connect(self.edit_control.redo)
            self.edit_control.document().redoAvailable.connect(
                self.action_Edit_Redo.setEnabled
            )
        if hasattr(self, "action_Font"):
            self.action_Font.triggered.connect(self.standard_font_choice)
        if hasattr(self, "action_Font_Color"):
            self.action_Font_Color.triggered.connect(self.standard_color_picker)
        QApplication.clipboard().dataChanged.connect(self.standard_clipboard_data_changed)
        self.edit_control.document().modificationChanged.connect(self.setWindowModified)

    def initialize_editing(self):
        if hasattr(self, "action_File_Save"):
            self.action_File_Save.setEnabled(self.edit_control.document().isModified())
        if hasattr(self, "action_Edit_Undo"):
            self.action_Edit_Undo.setEnabled(
                self.edit_control.document().isUndoAvailable()
            )
        if hasattr(self, "action_Edit_Redo"):
            self.action_Edit_Redo.setEnabled(
                self.edit_control.document().isRedoAvailable()
            )
        if hasattr(self, "action_Edit_Cut"):
            self.action_Edit_Cut.setEnabled(False)
        if hasattr(self, "action_Edit_Copy"):
            self.action_Edit_Copy.setEnabled(False)
        if hasattr(self, "font_changed"):
            self.font_changed(self.edit_control.font())
        if hasattr(self, "color_changed"):
            self.color_changed(self.edit_control.textColor())
        self.setWindowModified(self.edit_control.document().isModified())

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
        self.combo_Font_Size.setCurrentIndex(self.combo_Font_Size.findText(f"{QApplication.font().pointSize()}"))


__all__ = ("GWStandardApp","GWStandardEditorApp")
