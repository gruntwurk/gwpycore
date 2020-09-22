from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtWidgets import QColorDialog, QFileDialog
from gwpycore.gw_gui.gw_gui_dialogs import ask_user_to_confirm, inform_user
import webbrowser
from gwpycore import ICON_WARNING


class CoreActions:
    """
    This is a (third) super class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        action_About
        action_Report_Bug
        action_Print_Preview and action_Export_Pdf
        action_Quit
        action_Help
        action_Updates
        action_Inspect_Config
        action_Distraction_Free
        action_Cycle_Skin and action_Previous_Skin
        action_Cycle_Syntax_scheme and action_Previous_Syntax_scheme
    """

    def __init__(self) -> None:
        self.currentColor = QColor()
        self.color_change_callback = None

    def not_implemented(self):
        inform_user(
            "Sorry, this feature is curently not available.",
            ICON_WARNING,
            parent=self,
            title="Not Implemented",
        )

    def about(self):
        if hasattr(self.config, "application_title"):
            info = f"{self.config.application_title}\nVersion: {self.config.version}"
            inform_user(info, parent=self, title="About")

    def report_bug(self):
        if hasattr(self.config, "report_bug_url"):
            webbrowser.open(self.config.report_bug_url, new=2)
        else:
            self.not_implemented()

    def home_page(self):
        if hasattr(self.config, "documentation_url"):
            webbrowser.open(self.config.documentation_url, new=2)
        else:
            self.not_implemented()

    def check_for_updates(self):
        if hasattr(self.config, "latest_release_url"):
            # FIXME Scrape the version number from self.latest_release_url
            self.not_implemented()
        else:
            self.not_implemented()

    def color_picker(self):
        new_color = QColorDialog.getColor(initial=self.currentColor, parent=self)
        if new_color.isValid():
            self.currentColor = new_color
        if self.color_change_callback:
            self.color_change_callback()

    def full_screen(self):
        # FIXME full_screen
        self.not_implemented()

    def close_application(self):
        if not self.config.confirm_exit:
            self.close()
        if ask_user_to_confirm("Exit, are you sure?", parent=self):
            self.close()
        # FIXME closes anyway

    def inspect_config(self):
        info = []
        for key, value in vars(self.config).items():
            info.append(f"{key} \t= {value.__repr__()}")
        info.sort()
        inform_user("\n".join(info), parent=self, title="Diagnostic: Configuration Settings")

    def print_preview(self):
        if not self.edit_control:
            return
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.show_preview)
        preview.exec_()

    def export_pdf(self):
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

    def connect_core_actions(self):
        """
        Attaches default handlers to any/all of the following actions, if they exist:
            * action_About
            * action_Report_Bug (links to a web page)
            * action_Print_Preview and action_Export_Pdf
            * action_Quit
            * action_Help (links to a web page)
            * action_Updates (checking for...)
            * action_Inspect_Config (on the Debug menu)
            * action_Distraction_Free (aka. Full Screen)
            * action_Cycle_Skin and action_Previous_Skin
            * action_Cycle_Syntax_scheme and action_Previous_Syntax_scheme
        """
        if hasattr(self, "action_About"):
            self.action_About.triggered.connect(self.about)
        if hasattr(self, "action_Report_Bug"):
            self.action_Report_Bug.triggered.connect(self.report_bug)
        if hasattr(self, "action_Export_Pdf"):
            self.action_Export_Pdf.triggered.connect(self.export_pdf)
        if hasattr(self, "action_Print_Preview"):
            self.action_Print_Preview.triggered.connect(self.print_preview)
        if hasattr(self, "action_Quit"):
            self.action_Quit.triggered.connect(self.close_application)
        if hasattr(self, "action_Help"):
            self.action_Help.triggered.connect(self.home_page)
        if hasattr(self, "action_Updates"):
            self.action_Updates.triggered.connect(self.check_for_updates)
        if hasattr(self, "action_Inspect_Config"):
            self.action_Inspect_Config.triggered.connect(self.inspect_config)
        if hasattr(self, "action_Distraction_Free"):
            self.action_Distraction_Free.triggered.connect(self.full_screen)
        if hasattr(self, "action_Cycle_Skin"):
            self.action_Cycle_Skin.triggered.connect(self.skins.next_skin)
        if hasattr(self, "action_Previous_Skin"):
            self.action_Previous_Skin.triggered.connect(self.skins.previous_skin)
        if hasattr(self, "action_Cycle_Syntax_scheme"):
            self.action_Cycle_Syntax_scheme.triggered.connect(self.syntax_schemes.next_syntax_scheme)
        if hasattr(self, "action_Previous_Syntax_scheme"):
            self.action_Previous_Syntax_scheme.triggered.connect(self.syntax_schemes.previous_syntax_scheme)

__all__ = ("CoreActions",)
