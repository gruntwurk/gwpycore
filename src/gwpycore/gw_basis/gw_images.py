from pathlib import Path
from typing import Union
from PIL import Image
from .gw_files import file_type_per_ext, filename_variation

DEFAULT_THUMBNAIL_SIZE = 128, 128

def make_thumbnail(original_filename: Union[Path, str], destination_filename: Union[Path, str] = "", size=DEFAULT_THUMBNAIL_SIZE):
    """
    Copies the given image file, resizing it in the process. If no destination
    filename is given, then one is created which includes the new size. If no
    size is specified, then 128 x 128 is assumed.
    """
    file_type = file_type_per_ext(original_filename)
    if not destination_filename:
        destination_filename = filename_variation(original_filename, max(size))
    im = Image.open(original_filename)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(destination_filename, file_type)

