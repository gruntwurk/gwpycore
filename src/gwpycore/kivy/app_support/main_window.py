from kivy.core.window import Window
from gwpycore import GWConfigError

def get_app_position() -> dict:
    """
    Fetches the current position & size of the Kivy app's main window.

    :return: A dict with four entries where the values are `str`s containing integers.
    """
    return {"app_left": str(Window.left),
            "app_top":  str(Window.top),
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

    :raises GWConfigError: If any value is not a valid integer.
    """
    try:
        if source['app_left']:
            Window.left = int(source['app_left'])
        if source['app_top']:
            Window.top = int(source['app_top'])
        if source['app_width'] and source['app_height']:
            Window.size = (int(source['app_width']), int(source['app_height']))
    except ValueError:
        raise GWConfigError("Invalid number(s) encountered while attempting to set the position/size of the main window.")


__all__ = [
    "get_app_position",
    "set_app_position",
]