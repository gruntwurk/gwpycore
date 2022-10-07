import logging

from kivy.uix.camera import Camera

from gwpycore import GWError, CameraInfo
from gwpycore import inform_user

LOG = logging.getLogger("gwpy")


class GWCamera(Camera):
    '''
    Subclass of the Kivy Camera widget that automatically gets configured
    according to the CameraInfo() singleton (in gwpycore).
    '''
    def __init__(self, **kwargs):
        assert not self.play
        cam = CameraInfo()
        LOG.debug("cam = {}".format(cam))
        self.index = cam.adjusted_port
        if cam.width:
            self.resolution = (cam.width, cam.height)
        LOG.debug("self.resolution = {}".format(self.resolution))
        try:
            super().__init__(**kwargs)
        except AttributeError:
            if cam.port != 0:
                orig_port = cam.port
                cam.port = 0
                self.index = cam.adjusted_port
                try:
                    super().__init__(**kwargs)
                    inform_user(f"Camera #{orig_port} was not found. Using camera #0.")
                except AttributeError:
                    raise GWError("Unable to initialize any camera.")

    def close(self):
        self.play = False
        CameraInfo().close()


__all__ = [
    "GWCamera",
]