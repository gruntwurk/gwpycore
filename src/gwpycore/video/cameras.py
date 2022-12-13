import logging
import cv2

from gwpycore.core.environ import is_windows
from gwpycore.core.gw_typing import Singleton

MAX_PORT_NUMBER = 3
LOG = logging.getLogger("gwpy")


@Singleton
class CameraInfo():
    def __init__(self) -> None:
        self._port = 0
        self._width = 0
        self._height = 0
        self._video_capture = None
        self._available_cameras = {}

    @property
    def available_cameras(self):
        if not self._available_cameras:
            self._available_cameras = self.find_cameras()
        return self._available_cameras

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
        return self._port + (cv2.CAP_DSHOW if is_windows() else 0)

    @property
    def width(self):
        """
        The resolution width of the selected camera. If not set prior to
        calling open(), then this will be set to the camera's default.
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """
        The resolution height for the selected camera. If not set prior to
        calling open(), then this will be set to the camera's default.
        """
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
        current = (self.port, self.width, self.height)

        for port_number in range(max_port_number + 1):
            self._port = port_number
            LOG.debug("Inspecting port_number = {}".format(port_number))
            if not self.open():
                continue
            assert self._video_capture is not None
            is_reading, _ = self._video_capture.read()
            results[port_number] = (is_reading, self._width, self._height)
            self.close()
        self.port, self.width, self.height = current
        return results

    def close(self):
        return cv2.destroyAllWindows()

    def open(self) -> bool:
        """
        Opens the video capture device, and then either sets or gets the
        resolution. That is, if the height and width properties are set prior
        to calling this method, then those values will be used to set the
        device's resolution. Otherwise, whatever the device's default
        resolution is will be recorded in the height and width properties.

        :return: True if successfully opened.
        """
        # LOG.debug("self.adjusted_port = {}".format(self.adjusted_port))
        self._video_capture = cv2.VideoCapture(self.adjusted_port)
        if not self._video_capture.isOpened():
            return False
        if self._width:
            self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(self._width))
        else:
            self._width = self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        if self._height:
            self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self._height))
        else:
            self._height = self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return True

    def __str__(self) -> str:
        return f"CameraInfo: port {self.port} ({self.adjusted_port}), {self.width} x {self.height}"


__all__ = [
    "CameraInfo",
]
