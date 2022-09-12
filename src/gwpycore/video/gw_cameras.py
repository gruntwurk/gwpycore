import logging
import cv2
from sys import platform

from gwpycore.core.gw_exceptions import GWWarning
from gwpycore.core.gw_typing import Singleton

MAX_PORT_NUMBER = 3
LOG = logging.getLogger("main")


@Singleton
class CameraInfo():
    def __init__(self) -> None:
        self.available_cameras = self.find_cameras()

        # We haven't picked a camera yet
        self._port = None
        self._width = 0
        self._height = 0
        self._camera = None

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
        if self._port is None:
            return None
        is_windows = platform == "win32"
        return self._port + (cv2.CAP_DSHOW if is_windows else 0)

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
        NOTE: The width/height are the CURRENT settings, not nec. the max resolution.

        """
        # TODO How do we get the name of the camera device?
        results = {}
        for port_number in range(max_port_number + 1):
            self._port = port_number
            LOG.debug("Inspecting port_number = {}".format(port_number))
            if not self.open():
                continue
            assert self._camera is not None
            is_reading, _ = self._camera.read()
            results[port_number] = (is_reading, self._width, self._height)
            self.close()
        return results

    def close(self):
        assert self._camera is not None
        return cv2.destroyAllWindows()

    def open(self) -> bool:
        LOG.debug("self.adjusted_port = {}".format(self.adjusted_port))
        self._camera = cv2.VideoCapture(self.adjusted_port)
        if not self._camera.isOpened():
            return False
        self._width = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self._height = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return True

    def set_available_camera(self, requested_port: int = None, width=None, height=None):
        """
        Determines the "best" camera port to use and selects it.

        :param requested_port: if `requested_port` is specified and it's one of
        the available cameras, then that one is selected, for sure. If it's not
        specified, or not available, then this picks the camera with the highest
        resolution (as was current when find_cameras was called).

        :raises GWWarning: If no cameras are found at all.
        """
        LOG.debug("requested_port = {}".format(requested_port))
        if len(self.available_cameras) <= 0:
            raise GWWarning("No cameras available. Nothing selected.")

        best_port = requested_port
        if best_port not in self.available_cameras.keys():
            highest_resolution_so_far = 0
            for port in self.available_cameras:
                _, w, h = self.available_cameras[port]
                if w * h > highest_resolution_so_far:
                    highest_resolution_so_far = w * h
                    best_port = port

        self._port = best_port
        LOG.debug("best_port = {}".format(best_port))
        if self.open():
            assert self._camera is not None
            if width and width != self._width:
                self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
                # The setter might not "take", so we have to requery
                self._width = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            if height and height != self._height:
                self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
                # The setter might not "take", so we have to requery
                self._height = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __str__(self) -> str:
        count = len(self.available_cameras)
        description = [f"{count} available cameras {self.available_cameras}."]
        if count:
            description.append(f"Currently selected: port {self.port}, {self.width} x {self.height}")
        else:
            description.append("No camera is currently selected.")
        return "\n".join(description)


__all__ = [
    "CameraInfo",
]
