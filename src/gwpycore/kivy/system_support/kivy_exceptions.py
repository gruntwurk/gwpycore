from kivy.base import ExceptionHandler, ExceptionManager
from gwpycore import log_uncaught


class GWKivyExceptionHandler(ExceptionHandler):
    EX_OK = 0  # keep runnning
    EX_WARNING = 1  # keep runnning
    EX_ERROR = 2  # (or higher) quit the app
    """
    This handler is added to the bottom of the kivy exception handler stack,
    and thus called if none of kivy's internal handlers were applicable. That
    means we're looking at a non-Kivy Exception that should have been caught
    somewhere within our application code but wasn't. So, we use GruntWurk's
    log_uncaught() function to sort it out.
    """
    def handle_exception(self, inst):
        exitcode = log_uncaught(inst)
        if exitcode < self.EX_ERROR:
            return ExceptionManager.PASS
        return ExceptionManager.RAISE


def manage_uncaught_exceptions_within_kivy():
    ExceptionManager.add_handler(GWKivyExceptionHandler())


__all__ = [
    "manage_uncaught_exceptions_within_kivy",
]