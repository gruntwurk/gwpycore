from pathlib import Path
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QTextCursor, QTextDocumentWriter
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtWidgets import QAction, QApplication, QColorDialog, QComboBox, QFileDialog, QFontComboBox, QFontDialog, QMenuBar, QTableWidgetItem, QTextEdit, QToolBar
from gwpycore.gw_gui.gw_gui_dialogs import InspectionDialog, ask_user_to_confirm, inform_user, show_information
import webbrowser
from gwpycore import ICON_WARNING

class GWStandardApp():
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
        If a the menu bar is redered invisble, then all of the actions will be inaccessible, unless...
        * The action is also associated with another widget (e.g. a toolbar) that is still visible, or
        * The action is directly added to the window (widget) -- which is what we're doing here.
        """
        menubar = self.findChild(QMenuBar)
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

    def standard_show_help(self):
        help_text_path = self.asset_root() / "help/help.html"
        if help_text_path.exists():
            with help_text_path.open("r") as f:
                show_information(f.read(),parent=self)
        elif hasattr(self.config, "documentation_url"):
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
        screen_no = QApplication.desktop().screenNumber(self)
        full_screen = QApplication.desktop().availableGeometry(screen_no)
        if hasattr(self,"original_geometry") and (self.geometry() == full_screen):
            self.setGeometry(self.original_geometry)
        else:
            self.original_geometry = self.geometry()
            self.setGeometry(full_screen)
        self.show()

    def standard_hide_menu(self):
        menubar = self.findChild(QMenuBar,"menubar")
        menubar.setVisible(not menubar.isVisible())

    def standard_inspect_config(self):
        sorted_keys = []
        sorted_keys.extend(vars(self.config).keys())
        sorted_keys.sort()
        inspector = InspectionDialog(prompt="The current configuration is:", title="Diagnostic: Configuration Settings", rows=len(sorted_keys), cols=2)
        for i, key in enumerate(sorted_keys):
            value = self.config.__dict__[key]
            inspector.info.setItem(i,0,QTableWidgetItem(key))
            inspector.info.setItem(i,1,QTableWidgetItem(value.__repr__()))
        inspector.exec_()

    def connect_standard_actions(self):
        if hasattr(self, "action_about"):
            self.action_about.triggered.connect(self.standard_about)
        if hasattr(self, "action_report_bug"):
            self.action_report_bug.triggered.connect(self.standard_report_bug)
        if hasattr(self, "action_quit"):
            self.action_quit.triggered.connect(self.standard_close_application)
        if hasattr(self, "action_help"):
            self.action_help.triggered.connect(self.standard_show_help)
        if hasattr(self, "action_updates"):
            self.action_updates.triggered.connect(self.standard_check_for_updates)
        if hasattr(self, "action_inspect_config"):
            self.action_inspect_config.triggered.connect(self.standard_inspect_config)
        if hasattr(self, "action_distraction_free"):
            self.action_distraction_free.triggered.connect(self.standard_full_screen)
        if hasattr(self, "action_hide_menu"):
            self.action_hide_menu.triggered.connect(self.standard_hide_menu)
        if hasattr(self, "action_cycle_skin"):
            self.action_cycle_skin.triggered.connect(self.skins.next_skin)
        if hasattr(self, "action_previous_skin"):
            self.action_previous_skin.triggered.connect(self.skins.previous_skin)
        if hasattr(self, "action_inspect_skin"):
            self.action_inspect_skin.triggered.connect(self.skins.inspect_skin)

    def disconnect_all(self, signal):
        while True:
            try:
                signal.disconnect()
            except TypeError:
                break



class GWStandardEditorApp(GWStandardApp):
    """
    This is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        All of the actions handled by GWStandardApp, plus:
        action_cycle_syntax_scheme and action_previous_syntax_scheme
        action_print_preview and action_export_pdf
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
        if hasattr(self, "action_edit_paste"):
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

        if hasattr(self, "action_export_pdf"):
            self.action_export_pdf.triggered.connect(self.standard_export_pdf)
        if hasattr(self, "action_file_save"):
            self.action_file_save.triggered.connect(self.standard_file_save)
            self.edit_control.document().modificationChanged.connect(
                self.action_file_save.setEnabled
            )
        if hasattr(self, "action_file_save_as"):
            self.action_file_save_as.triggered.connect(self.standard_file_save_as)
        if hasattr(self, "action_print_preview"):
            self.action_print_preview.triggered.connect(self.standard_print_preview)
        if hasattr(self, "action_cycle_syntax_scheme"):
            self.action_cycle_syntax_scheme.triggered.connect(
                self.syntax_schemes.next_syntax_scheme
            )
        if hasattr(self, "action_previous_syntax_scheme"):
            self.action_previous_syntax_scheme.triggered.connect(
                self.syntax_schemes.previous_syntax_scheme
            )
        if hasattr(self, "action_edit_copy"):
            self.action_edit_copy.triggered.connect(self.edit_control.copy)
            self.edit_control.copyAvailable.connect(self.action_edit_copy.setEnabled)
        if hasattr(self, "action_edit_cut"):
            self.action_edit_cut.triggered.connect(self.edit_control.cut)
            self.edit_control.copyAvailable.connect(self.action_edit_cut.setEnabled)
        if hasattr(self, "action_edit_paste"):
            self.action_edit_paste.triggered.connect(self.edit_control.paste)
        if hasattr(self, "action_edit_undo"):
            self.action_edit_undo.triggered.connect(self.edit_control.undo)
            self.edit_control.document().undoAvailable.connect(
                self.action_edit_undo.setEnabled
            )
        if hasattr(self, "action_edit_redo"):
            self.action_edit_redo.triggered.connect(self.edit_control.redo)
            self.edit_control.document().redoAvailable.connect(
                self.action_edit_redo.setEnabled
            )
        if hasattr(self, "action_font"):
            self.action_font.triggered.connect(self.standard_font_choice)
        if hasattr(self, "action_font_color"):
            self.action_font_color.triggered.connect(self.standard_color_picker)
        QApplication.clipboard().dataChanged.connect(self.standard_clipboard_data_changed)
        self.edit_control.document().modificationChanged.connect(self.setWindowModified)

    def initialize_editing(self):
        if hasattr(self, "action_file_save"):
            self.action_file_save.setEnabled(self.edit_control.document().isModified())
        if hasattr(self, "action_edit_undo"):
            self.action_edit_undo.setEnabled(
                self.edit_control.document().isUndoAvailable()
            )
        if hasattr(self, "action_edit_redo"):
            self.action_edit_redo.setEnabled(
                self.edit_control.document().isRedoAvailable()
            )
        if hasattr(self, "action_edit_cut"):
            self.action_edit_cut.setEnabled(False)
        if hasattr(self, "action_edit_copy"):
            self.action_edit_copy.setEnabled(False)
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
