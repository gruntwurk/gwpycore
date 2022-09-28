from kivy.app import App
from kivy.uix.screenmanager import Screen
from ..app_support.screens import switch_to_screen

__all__ = [
    "GWScreen",
]


class GWScreen(Screen):
    def __init__(self, **kw):
        self.app: App = None
        self._previous_screen = 'main_screen'
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app: App = App.get_running_app()
        return super().on_pre_enter(*args)

    @property
    def previous_screen(self):
        """The name of the screen to return to when this screen is closed/canceled."""
        return self._previous_screen

    @previous_screen.setter
    def previous_screen(self, value):
        self._previous_screen = value

    def cancel(self):
        self.close()

    def close(self):
        switch_to_screen(self._previous_screen)
