import webbrowser
from gwpycore import ICON_WARNING, ask_user_to_confirm, inform_user


class CoreActions:
    """
    This super class that can be a (third) class from which a QDialog can 
    inherit. It provides default handlers for a half dozen functions 
    (About, Help, etc.)
    """
    def __init__(self) -> None:
        self.confirm_exit = True
        self.documentation_url = ""
        self.report_bug_url = ""
        self.latest_release_url = ""
        self.application_title = ""
        self.version = "Unknown"

    def not_implemented(self):
        inform_user(
            "Sorry, this feature is curently not available.",
            ICON_WARNING,
            parent=self,
            title="Not Implemented",
        )

    def about(self):
        inform_user(
            f"{self.application_title}\nVersion: {self.version}",
            parent=self,
            title="About",
        )

    def report_bug(self):
        if self.report_bug_url:
            webbrowser.open(self.report_bug_url, new=2)
        else:
            self.not_implemented()

    def home_page(self):
        if self.documentation_url:
            webbrowser.open(self.documentation_url, new=2)
        else:
            self.not_implemented()

    def check_for_updates(self):
        if self.latest_release_url:
            # FIXME Scrape the version number from self.latest_release_url
            self.not_implemented()
        else:
            self.not_implemented()

    def full_screen(self):
        # FIXME full_screen
        self.not_implemented()

    def close_application(self):
        if not self.confirm_exit:
            self.close()
        if ask_user_to_confirm("Exit, are you sure?", parent=self):
            self.close()

    def connect_core_actions(self):
        self.action_About.triggered.connect(self.about)
        self.action_Bug.triggered.connect(self.report_bug)
        self.action_Exit.triggered.connect(self.close_application)
        self.action_Help.triggered.connect(self.home_page)
        self.action_Updates.triggered.connect(self.check_for_updates)
        self.action_Distraction_Free.triggered.connect(self.full_screen)


__all__ = ("CoreActions",)