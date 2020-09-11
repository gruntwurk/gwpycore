import webbrowser
from gwpycore import ICON_WARNING, ask_user_to_confirm, inform_user


class CoreActions:
    """
    This super class that can be a (third) class from which a QDialog can inherit.
    It connects default handlers to any of the following actions that exist:
        action_About
        action_Report_Bug
        action_Exit
        action_Help
        action_Updates
        action_Inspect_Config
        action_Distraction_Free
    """

    def __init__(self) -> None:
        pass

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

    def connect_core_actions(self):
        if hasattr(self, "action_About"):
            self.action_About.triggered.connect(self.about)
        if hasattr(self, "action_Report_Bug"):
            self.action_Report_Bug.triggered.connect(self.report_bug)
        if hasattr(self, "action_Exit"):
            self.action_Exit.triggered.connect(self.close_application)
        if hasattr(self, "action_Help"):
            self.action_Help.triggered.connect(self.home_page)
        if hasattr(self, "action_Updates"):
            self.action_Updates.triggered.connect(self.check_for_updates)
        if hasattr(self, "action_Inspect_Config"):
            self.action_Inspect_Config.triggered.connect(self.inspect_config)
        if hasattr(self, "action_Distraction_Free"):
            self.action_Distraction_Free.triggered.connect(self.full_screen)


__all__ = ("CoreActions",)
