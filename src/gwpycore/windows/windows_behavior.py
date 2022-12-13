import pywintypes  # noqa -- DO NOT REMOVE -- This is a hint for PyInstaller
import win32con
import win32gui


class WindowsBehaviorAdjuster:
    """
    Utility object for adjusting Windows-specific behavior that can interfere
    with an application.

    :param log: (optional) a logger (logging.getLogger(foo)) to which
    DIAGNOSTIC messages will be sent detailing what is being done, exactly.
    """

    def __init__(self, log=None) -> None:
        self.log = log
        self.initialWindowTracking = False

    def disableWindowTracking(self, log):
        """disableWindowTracking"""
        try:
            self.initialWindowTracking = win32gui.SystemParametersInfo(win32con.SPI_GETACTIVEWINDOWTRACKING)
        except Exception as e:
            if self.log:
                self.log.exception(e)

        if self.initialWindowTracking:
            if self.log:
                self.log.diagnostic("Window Tracking was initially enabled. Disabling it for the duration; will re-enable on exit.")
            win32gui.SystemParametersInfo(win32con.SPI_SETACTIVEWINDOWTRACKING, False)
        else:
            if self.log:
                self.log.diagnostic("Window Tracking is already disabled. No adjustment needed.")

    def __del__(self):
        # This method is automatically called when this object is deleted (i.e. when the last reference is gone).
        if self.initialWindowTracking:
            if self.log:
                self.log.diagnostic(f"Restoring initial window tracking behavior ({self.initialWindowTracking})")
            win32gui.SystemParametersInfo(win32con.SPI_SETACTIVEWINDOWTRACKING, self.initialWindowTracking)


__all__ = [
    "WindowsBehaviorAdjuster",
]
