from PyQt5.QtWidgets import QAction
import pytest
from gwpycore import AppActions


@pytest.fixture
def app_actions():
    return AppActions(None)


def test_addAction(app_actions):
    app_actions.addAction("quit", "&Quit", "Ctrl+q", "Alt+x", tip="Leave the application")
    action: QAction = app_actions.quit
    # FIXME assert action.text == "&Quit"
    # assert action.toolTip == "Leave the application"
    # assert action.shortcuts.length == 2

