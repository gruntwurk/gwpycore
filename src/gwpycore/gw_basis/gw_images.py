from pathlib import Path
from typing import Union
from PIL import Image
from .gw_files import file_type_per_ext, filename_variation

DEFAULT_THUMBNAIL_SIZE = 128, 128
DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1200
TEMP_FILE = '_temp.jpg'


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


def limited_size_version(filespec: Union[Path, str], max_width=DEFAULT_MAX_WIDTH, max_height=DEFAULT_MAX_HEIGHT) -> Path:
    """
    If the given filespec is for an image that is already smaller than the
    stated maximums, then we just pass along that filespec. Otherwise, we copy
    the file resized as a temp file and return the name of that temp file.
    """
    filespec = Path(filespec)
    image = Image.open(filespec)
    w = image.size[0]
    h = image.size[1]
    if h <= max_height and w <= max_width:
        return filespec
    reduction_percent = min((max_height / float(h)), (max_width / float(w)))
    new_height = int((float(h) * float(reduction_percent)))
    new_width = int((float(w) * float(reduction_percent)))
    image = image.resize((new_width, new_height), Image.NEAREST)
    temp_filespec = filespec.parent / TEMP_FILE
    image.save(temp_filespec)
    return temp_filespec


__all__ = [
    "make_thumbnail",
    "limited_size_version",
]