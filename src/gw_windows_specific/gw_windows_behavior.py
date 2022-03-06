import logging

import pywintypes  # DO NOT REMOVE -- This is a hint for PyInstaller
import win32con
import win32gui

LOG = logging.getLogger("main")


class WindowsBehaviorAdjuster:
    """Utility object for adjusting Windows-specific behavior that can interefere with an application."""

    def __init__(self) -> None:
        self.initialWindowTracking = False

    def disableWindowTracking(self):
        """disableWindowTracking"""
        try:
            self.initialWindowTracking = win32gui.SystemParametersInfo(win32con.SPI_GETACTIVEWINDOWTRACKING)
        except:
            pass
        if self.initialWindowTracking:
            LOG.diagnostic("Window Tracking was initially enabled. Disabling it for the duration; will re-enable on exit.")
            win32gui.SystemParametersInfo(win32con.SPI_SETACTIVEWINDOWTRACKING, False)
        else:
            LOG.diagnostic("Window Tracking is already disabled. No adjustment needed.")

    def __del__(self):
        # This method is automatically called when this object is deleted (i.e. when the last referece is gone).
        if self.initialWindowTracking:
            LOG.diagnostic(f"Restoring initial window tracking behavior ({self.initialWindowTracking})")
            win32gui.SystemParametersInfo(win32con.SPI_SETACTIVEWINDOWTRACKING, self.initialWindowTracking)


__all__ = ("WindowsBehaviorAdjuster",)
