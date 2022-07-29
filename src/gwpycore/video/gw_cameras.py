import cv2
from sys import platform

from gwpycore.core.gw_exceptions import GWWarning
from gwpycore.core.gw_typing import Singleton

MAX_PORT_NUMBER = 3


@Singleton
class CameraInfo():
    def __init__(self) -> None:
        self.available_cameras = self.find_cameras()

        # We haven't picked a camera yet
        self._port = None
        self._adjusted_port = None
        self._width = 0
        self._height = 0

    @property
    def port(self):
        """
        The port number for the selected camera. Zero-based. Default is None.
        """
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def adjusted_port(self):
        """
        The adjusted port number for the selected camera. Adjusted means that
        the port number is ammended to specify the driver source (e.g.
        DirectShow on Windows).
        """
        return self._adjusted_port

    @adjusted_port.setter
    def adjusted_port_number(self, value):
        self._adjusted_port = value

    @property
    def width(self):
        """The resolution width of the selected camera. Default is 0."""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """The resolution height of the selected camera. Default is 0."""
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def find_cameras(self, max_port_number=MAX_PORT_NUMBER):
        """
        Tests the camera ports and returns a dictionary of the available ports and
        their status.

        :param max_port_number: The highest port number to test. Default is 3.

        :return: A dictionary where the key is the port number (0-based). The
        value is a tuple: (is_active, width, height). True means the camera is
        turned on. False means the camera is working, but not turned on. Either
        way, the width and height will be the camera's resolution.
        (If there is no camera attached to a given port, then it will not be
        listed in the dictionary at all.)
        """
        # TODO How do we get the name of the camera device?
        is_windows = platform == "win32"
        results = {}
        for port_number in range(max_port_number + 1):
            camera = cv2.VideoCapture(port_number + (cv2.CAP_DSHOW if is_windows else 0))
            if not camera.isOpened():
                continue
            is_reading, _ = camera.read()
            w = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            results[port_number] = (is_reading, w, h)
        return results

    def set_available_camera(self, requested_port: int = None):
        """
        Determines the "best" camera port to use and selects it.

        :param requested_port: if `requested_port` is specified and it's one of
        the available cameras, then that one is selected, for sure. If it's not
        specified, or not available, then this picks the camera with the highest
        resolution.

        :raises GWWarning: If no cameras are found at all.
        """
        is_windows = platform == "win32"
        if len(self.available_cameras) <= 0:
            raise GWWarning("No cameras available. Nothing selected.")

        best_port = requested_port
        if best_port not in self.available_cameras:
            highest_width_so_far = 0
            for port in self.available_cameras:
                _, w, _ = self.available_cameras[port]
                if w > highest_width_so_far:
                    highest_width_so_far = w
                    best_port = port

        self._port = best_port
        _, self._width, self._height = self.available_cameras[best_port]
        self._adjusted_port = best_port + (cv2.CAP_DSHOW if is_windows else 0)


__all__ = [
    "CameraInfo",
]
