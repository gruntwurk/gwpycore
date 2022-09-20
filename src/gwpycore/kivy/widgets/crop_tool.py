"""
CropTool widget -- Allows for an image to be zoomed in/out and panned right/left/up/down.
"""
import logging
from pathlib import Path
from PIL import Image as PilImage
from typing import Tuple, Union

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ReferenceListProperty, Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import Canvas
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.texture import Texture

LOG = logging.getLogger("gwpy")
ZOOM_INCREMENT = 0.1 # make the image 10% bigger or smaller
DEFAULT_IMAGE_WINDOW_HEIGHT = 720
DEFAULT_IMAGE_WINDOW_WIDTH = 1280


# ############################################################################
#                                                                 IMAGE WINDOW
# ############################################################################

class ImageWindow(Widget):
    """
    The inner widget for the CropTool widget.
    """
    _image = None
    zoom_factor = 1.0
    previous_zoom_factor = 0
    starting_pos = (0,0)
    move_by = (0,0)
    accumulated_move_by = (0,0)
    proposed_crop_size = (0,0)

    def __init__(self, source, aspect_ratio=1, **kwargs):
        # LOG.debug(f"Initializing image_window: {source}")
        self.source = source
        self._aspect_ratio = aspect_ratio
        self.size_hint = (1.0, 1.0)
        super().__init__(**kwargs)

    @property
    def image(self) -> Image:
        if not self._image:
            self._image = Image(source=self._source, allow_stretch=False)
            self._image.size_hint = (1.0, 1.0)
            self.add_widget(self._image)
            self._image.size = self.get_limited_size()
            self.repaint()
        return self._image

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value: Union[Path, str]):
        self._source = str(value)
        if self._image:
            self._image.source = self._source
        self.previous_zoom_factor = 0

    def get_limited_size(self):
        # LOG.debug(f"self.aspect_ratio = {self.aspect_ratio}")
        lsize = (self.height * self._aspect_ratio, self.height)
        # LOG.debug(f"Limited size = {lsize}")
        return lsize

    def on_size(self, *args):
        # LOG.debug(f"image_window resized to {self.size}")
        self.image.pos_hint = {'x': 1, 'y': 1}
        self.image.size = self.get_limited_size()
        # LOG.debug(f"image itself resized to {self.image.size}")
        self.repaint()

    def on_touch_move(self, touch):
        # LOG.debug(f"on_touch_move {touch.button} {touch.pos} {touch.profile}")
        starting_x, starting_y = self.starting_pos
        accumulated_x, accumulated_y = self.accumulated_move_by

        self.move_by = (accumulated_x + touch.x - starting_x, accumulated_y + touch.y - starting_y)
        self.repaint()
        return super(ImageWindow, self).on_touch_move(touch)

    def on_touch_down(self, touch):
        '''
        Event handler that looks for the mouse's scroll wheel being
        manipulated while the mouse hovers over the image.
        '''
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'scrollup':
                    self.zoom(-ZOOM_INCREMENT)
                elif touch.button == 'scrolldown':
                    self.zoom(ZOOM_INCREMENT)
                elif touch.button == 'left':
                    self.start_move(touch.pos)
            return True # handled
        return super(ImageWindow, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.end_move()

    def start_move(self, pos):
        self.starting_pos = pos

    def end_move(self):
        if self.starting_pos:
            self.starting_pos = None
            self.accumulated_move_by = self.move_by

    def zoom(self, factor):
        '''
        Zooms the image in or out. A positive factor zooms the image in.
        A negative one zooms it back out.
        A factor of 0 resets the zoom to the original size.
        '''
        if factor == 0:
            self.zoom_factor = 1.0
        else:
            self.zoom_factor += factor
        if self.zoom_factor < 1:
            self.zoom_factor = 1.0
        # LOG.debug(f"self.zoom_factor {self.zoom_factor}")
        if self.previous_zoom_factor != self.zoom_factor:
            self.previous_zoom_factor = self.zoom_factor
            self.repaint()

    def notify_proposed_dimensions(self, crop_size):
        self.proposed_crop_size = crop_size
        zoom_image: CropTool = self.parent
        zoom_image.notify_proposed_dimensions(self.proposed_crop_size)

    def crop_photo(self, photo_folder, original_photo_filename, new_photo_filename):
        folder = Path(photo_folder)
        orig_image = PilImage.open(folder / original_photo_filename)
        pos,size = self.crop_specs()
        box = self.bounding_box_for_pil(pos, size, orig_image.height)
        cropped_image = orig_image.crop(box)
        cropped_image.save(folder / new_photo_filename)
        self.source = folder / new_photo_filename
        self.reset_zooming()
        self.repaint()

    def bounding_box_for_pil(self, pos, size, orig_height):
        """
        IMPORTANT: Pillow coordinates are upside down!  (0,0 being UPPER left)

        :param pos: x,y in normal coordinates (0,0 being lower left)
        :param size: w,h of area to be cropped
        :return: (left, upper, right, lower)
        """
        x,y = pos
        w,h = size
        LOG.debug("(x,y,w,h) = {}".format((x,y,w,h)))
        # assert x >= 0 and y >= 0
        assert w > 0 and h > 0
        box = (x, orig_height - (y+h), x+w, orig_height - y)
        return box

    def reset_zooming(self):
        self.zoom_factor = 1.0
        self.move_by = (0,0)
        self.previous_zoom_factor = 0
        self.starting_pos = None
        self.accumulated_move_by = (0, 0)
        self.proposed_crop_size = (0, 0)


    def crop_specs(self):
        """
        The x,y,w,h factors that correspond to how the image is currently
        zoomed/panned, so that the original image can be cropped accordingly.

        :return: ((x, y), (w, h))
        """
        default_result = ((0, 0), (self.width, self.height))
        if not self._image:
            return default_result
        t: Texture = self.image.texture
        if not t:
            return default_result
        w, h = t.size
        cropped_width = int(min(w, h * self._aspect_ratio) / self.zoom_factor)
        cropped_height = int(h / self.zoom_factor)
        move_x, move_y = self.move_by
        crop_pos_x = int((w - cropped_width) / 2 - move_x)
        crop_pos_y = int((h - cropped_height) / 2 - move_y)
        return ((crop_pos_x, crop_pos_y), (cropped_width, cropped_height))

    def repaint(self):
        # LOG.debug(f"Repaint called")
        t: Texture = self.image.texture
        if not t:
            return
        crop_pos, crop_size = self.crop_specs()
        # LOG.debug(f"Crop specs: {crop_pos} {crop_size}")
        self.notify_proposed_dimensions(crop_size)
        subtexture = t.get_region(*crop_pos, *crop_size)
        limited_width, limited_height = self.get_limited_size()
        # LOG.debug(f"Limited size: {limited_width} {limited_height}")
        left_margin = (self.width - limited_width)/2

        c: Canvas = self.canvas
        # LOG.debug(f"image_window.pos {self.pos}")
        # LOG.debug(f"image_window.size {self.size}")
        c.clear()
        c.add(Color(1, 1, 1))
        self.x = self.parent.x
        self.y = self.parent.y
        c.add(Rectangle(texture=subtexture, pos=(self.x + left_margin, self.y), size=(limited_width, limited_height)))
        c.ask_update()


# ############################################################################
#                                                                    CROP TOOL
# ############################################################################

class CropTool(BoxLayout):
    """
    This widget allows for an image to be cropped by zooming and panning.
    This widget is a BoxLayout that contains an ImageWindow (created just in time), which in turn contains an Image.
    The ImageWindow always fills this CropTool, but the Image can be smaller (usually narrower).
    The actual height and width of the target_size property is inconsequnetial.
    It's only used to determine the taget aspect ratio.
    """
    source = StringProperty()
    target_width = NumericProperty(DEFAULT_IMAGE_WINDOW_WIDTH)
    target_height = NumericProperty(DEFAULT_IMAGE_WINDOW_HEIGHT)
    target_size = ReferenceListProperty(target_width, target_height)
    _image_window: ImageWindow = None
    target_aspect_ratio = DEFAULT_IMAGE_WINDOW_WIDTH / DEFAULT_IMAGE_WINDOW_HEIGHT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def image_window(self):
        if not self._image_window:
            self._image_window = ImageWindow(self.source, self.target_aspect_ratio)
            self.add_widget(self._image_window)
        return self._image_window

    @property
    def crop_size(self) -> Tuple:
        _, size = self.image_window.crop_specs()
        return size

    def on_source(self, *args):
        # LOG.debug(f"ZoomImage on_source: {self.source}")
        self.image_window.source = self.source
        # LOG.debug(f"ZoomImage on_source repainting")
        self.image_window.repaint()

    def on_size(self, *args):
        # LOG.debug(f"ZoomImage on_size: {self.size}")
        self.image_window.size = self.size

    def on_target_size(self, *args):
        # LOG.debug(f"ZoomImage on_target_size: {self.target_size}")
        w, h = self.target_size
        self.target_aspect_ratio = w / h
        self.image_window._aspect_ratio = self.target_aspect_ratio

    def crop_photo(self, *args):
        self.image_window.crop_photo(*args)

    def notify_proposed_dimensions(self, crop_size):
        screen = self.parent.parent
        screen.display_proposed_dimensions(crop_size)


__all__ = [
    "CropTool",
]