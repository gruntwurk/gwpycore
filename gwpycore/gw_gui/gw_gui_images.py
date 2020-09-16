from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from gwpycore.gw_gui.gw_gui_theme import GWAssets

from typing import Union
from pathlib import Path

import logging

LOG = logging.getLogger("main")


class ImageAssets(GWAssets):
    """This class manages the content of the assets/images folder,
    and provides a simple interface for requesting images. Only images
    named in the given image map are handled.
"""

    def __init__(self, image_map, asset_path: Union[Path,str]):
        super().__init__(asset_path)

        self.image_map = image_map

    def apply_theme(self):
        # No themes for images
        pass

    def load_image(self, slug, width_px, height_px) -> QPixmap:
        """Load graphical image element based on the image map."""
        if slug not in self.image_map:
            LOG.error(f"Image with name '{slug}' does not exist")
            return QPixmap()

        img_path = self.asset_path / self.image_map[slug]
        if not img_path.isfile():
            LOG.error(
                f"Image file '{self.image_map[slug]}' not in assets folder"            )
            return QPixmap()

        image = QPixmap(img_path)
        if width_px and height_px:
            return image.scaled(width_px, height_px, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif width_px is None and height_px:
            return image.scaledToHeight(height_px, Qt.SmoothTransformation)
        elif width_px and height_px is None:
            return image.scaledToWidth(width_px, Qt.SmoothTransformation)

        return image
