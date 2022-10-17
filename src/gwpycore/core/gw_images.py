import logging
from pathlib import Path
from typing import Union
from PIL import Image, UnidentifiedImageError

from .gw_files import filename_variation

LOG = logging.getLogger("gwpy")

DEFAULT_THUMBNAIL_SIZE = 128
DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1200
TEMP_FILE = '_temp'


def make_thumbnail(original_filename: Union[Path, str], destination_filename: Union[Path, str] = "",
                   max_width=DEFAULT_THUMBNAIL_SIZE, max_height=DEFAULT_THUMBNAIL_SIZE):
    """
    Copies the given image file, resizing it in the process. If no size limits
    are specified, then 128 x 128 is assumed. If no destination filename is
    given, then one is created which includes the larger of the two size limits.
    (e.g. 'my_folder/my_image.png' -> 'my_folder/my_image_128.png')
    """
    if not destination_filename:
        destination_filename = filename_variation(original_filename, max(max_width, max_height))
    im = Image.open(original_filename)
    size = (max_width, max_height)
    im.thumbnail(size)
    try:
        im.save(destination_filename)
    except OSError:
        LOG.error("Unable to save {}".format(destination_filename))


def limited_size_version(filespec: Union[Path, str], max_width=DEFAULT_MAX_WIDTH, max_height=DEFAULT_MAX_HEIGHT) -> Path:
    """
    If the given filespec is for an image that is already smaller than the
    stated maximums, then we just pass along that filespec. Otherwise, we copy
    the file resized as a temp file and return the name of that temp file.
    Also, if PIL can't recognize the given file as being an image, then we
    just return the original filespec.

    :param filespec: The original image filespec.
    :param max_width: Maximum width constraint. Defaults to 1920.
    :param max_height: Maximum height constraint. Defaults to 1200.
    :return: Either the original image filespec, or the filespec of a reduced copy.
    """
    filespec = Path(filespec)
    if not filespec.exists():
        return None
    try:
        image = Image.open(filespec)
    except UnidentifiedImageError:
        return filespec

    w = image.size[0]
    h = image.size[1]
    if h <= max_height and w <= max_width:
        return filespec

    # This keeps the same filename suffix as the original (.JPG, .PNG, ...)
    temp_filespec = filespec.with_name(TEMP_FILE + filespec.suffix)
    make_thumbnail(filespec, temp_filespec, max_width, max_height)
    return temp_filespec


__all__ = [
    "make_thumbnail",
    "limited_size_version",
]