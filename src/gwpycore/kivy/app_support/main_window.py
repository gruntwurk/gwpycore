from kivy.core.window import Window

from ...core.exceptions import GWConfigSettingWarning


__all__ = [
    "widget_by_id",
    "get_app_position",
    "set_app_position",
]


def widget_by_id(parent, value) -> object:
    for widget in parent.walk():
        if widget.id == value:
            return widget
    return None


def get_app_position() -> dict:
    """
    Fetches the current position & size of the Kivy app's main window.

    :return: A dict with four entries where the values are `str`s containing integers.
    """
    return {"app_left": str(Window.left),
            "app_top": str(Window.top),
            "app_height": str(Window.height),
            "app_width": str(Window.width),
            }


def set_app_position(source: dict):
    """
    Sets a new position &/or size for the Kivy app's main window.

    :param source: A dict that should include the following keys: `app_left`,
    `app_top`, `app_height`, `app_width` -- all with integer values (`int` or a
    `str` containing an integer value). If any of those keys do not exist,
    then the corresponding aspect of the window will not change. (With
    height and width, it's both or nothing.)

    :raises GWConfigSettingWarning: If any value is not a valid integer.
    """
    try:
        if source['app_left']:
            Window.left = int(source['app_left'])
        if source['app_top']:
            Window.top = int(source['app_top'])
        if source['app_width'] and source['app_height']:
            Window.size = (int(source['app_width']), int(source['app_height']))
    except ValueError:
        raise GWConfigSettingWarning(
            key="(left, top, width, height)",
            attempted_value=f"({source['app_left']},{source['app_top']},{source['app_width']},{source['app_height']})",
            context="an attempt to set the position/size of the main window")


