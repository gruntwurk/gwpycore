"""
Functions:
    copy_file -- (same as in the deprecated distutils)
    move_file -- (same as in the deprecated distutils)
    write_file -- (same as in the deprecated distutils)
    enquote_spaces(file_name)
    file_type_per_ext(filespec)
    filename_variation(filespec, variation_descriptor) -- e.g. to add a timestamp to the file or dir name
    save_backup_file(source_file, backup_folder)
Directory-Related Utils:
    FileInventory class -- Analyzes the contents of a directory tree. Looks for duplicate files, etc.
See also:
    Path(filespec).touch()

"""
import distutils
import hashlib
import os
from time import sleep
from pathlib import Path
from typing import Union
import logging

from .exceptions import GWNotADirectoryError
from .datetime_utils import timestamp


__all__ = [
    "enquote_spaces",
    "file_type_per_ext",
    "filename_variation",
    "save_backup_file",
    "remove_file_when_released",
    "copy_file",
    "move_file",
    "touch",
    "as_path",
    "md5_digest",
]

LOG = logging.getLogger('gwpy')


# ############################################################################
# Since distutils is deprecated...                           SINGLE FILE UTILS
# ############################################################################

def copy_file(src, dst, preserve_mode=1, preserve_times=1, update=0, link=None, verbose=0, dry_run=0):
    """
    Copies a single file, src, to dst. (If the dst file already exists, it is
    ruthlessly clobbered.)

    :param src:

    :param dst: If `dst` is a directory, then `src` is copied there with the
    same name; otherwise, it must be a filename.

    :param preserve_mode: If true (1, the default), the file's mode (type and
    permission bits, or whatever is analogous on the current platform) is
    copied.

    :param preserve_times: If true (1, the default), the last-modified and
    last-access times are copied as well.

    :param update: If true (1), `src` will only be copied if `dst` does not
    exist, or if `dst` does exist but is older than `src`.

    :param link: allows you to make hard links(using os.link()) or symbolic links
    (using os.symlink()) instead of copying: set it to 'hard' or 'sym'.
    If it is None (the default), files are copied. Don't set link on
    systems that don't support it: copy_file() doesn't check if hard
    or symbolic linking is available. It uses _copy_file_contents()
    to copy file contents.

    :param verbose:

    :param dry_run:

    :returns: A tuple (`dest_name`, `copied`): `dest_name` is the actual name of the
        output file, and `copied` is true if the file was copied (or would have
        been copied, if dry_run is true).

    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    return distutils.file_util.copy_file(str(src), str(dst), preserve_mode, preserve_times, update, link, verbose, dry_run)


def move_file(src, dst, verbose=0, dry_run=0):
    """
    Moves a single file, src, to dst.

    Arguments:
        If dst is a directory, the file will be moved into it with the same name;
        otherwise, src is just renamed to dst.

    Returns:
        The new full name of the file.
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    return distutils.file_util.move_file(str(src), str(dst), verbose, dry_run)


def touch(filespec):
    filespec = Path(filespec)
    if filespec.exists():
        filespec.touch()


def remove_file_when_released(filespec) -> bool:
    # FIXME Not sure this is working as intended
    PAUSE_TIME = 0.1  # seconds
    LIMIT = 20  # 20 loops = 2 seconds
    for _ in range(LIMIT):
        try:
            os.remove(str(filespec))
            return True
        except PermissionError:
            sleep(PAUSE_TIME)
    return False


# ############################################################################
#                                                             ADDITIONAL UTILS
# ############################################################################

def as_path(input: any) -> Path:
    """
    Convert a string to a Path.
    This can be used to extend `ConfigParser` to understand `pathlib.Path` types.
    This is also useful for importing data from a text file (csv, tsv, fixed format, etc.)
    """
    p = input if isinstance(input, Path) else None
    if isinstance(input, str):
        p = Path(input)
    if p:
        p = p.expanduser()
    return p


def enquote_spaces(file_name: str) -> str:
    """
    Returns the given file name. If the name contains one or more spaces, then
    the name is first enclosed in double-quotes.
    """
    return f'"{file_name}"' if " " in file_name else file_name


def file_type_per_ext(filespec: Union[Path, str]) -> str:
    """
    Returns the file type based on a file name's extension (sans dot and
    converted to lower case).

    filespec: Either a Path, a string that names a file, or a string with just
        a file extension (leading dot).
    """
    return Path(filespec).suffix.casefold().replace(".", "")


def filename_variation(filespec, descriptor=timestamp(), suffix=None) -> str:
    """
    Given the name (or Path) of an original file, this returns a slightly
    modified (corresponding) filename (as a str). This filename variation is
    suitable, for example, for making a backup copy of the original file.

    :param descriptor: Text that will be added to the stem of the original
    filname. If no descriptor is specified, then a timestamp will be used.
    To supress the descriptor altogether, pass in "" or None.

    :parm suffix: The filename extension to use with the generated filename.
    Default is to use the same extension as the source file.

    :examples:
    filename_variation("README.txt") -> "README_2022_07_04_235959.txt"
    filename_variation("README.txt",suffix=".BAK") -> "README_2022_07_04_235959.BAK"
    filename_variation("README.txt", descriptor="original") -> "README_original.txt"
    filename_variation("README.txt", descriptor="", suffix=".original") -> "README.original"

    """
    filespec = Path(filespec)
    return str(filespec.with_name(filespec.stem + ("_" if descriptor else "") + str(descriptor) + (suffix or filespec.suffix)))


def save_backup_file(source_file: Path, backup_folder: Path = None, simple_bak=False, overwrite=True) -> str:
    """
    Makes a backup copy of the source file.

    :param backup_folder: Where to place the backup copy. The folder and its
    parents will be created first, if necessary. If no backup_folder is
    specified, then the backup will bve placed in the same folder as the
    original file.

    :param simple_bak: If True, the backup copy will be named simply by
    changing the file extension to ".bak"; otherwise, the default is to
    insert a timestamp into the name.

    :param overwrite: True (default) allows an existing backup file to
    be overwritten.

    :return: The name of the backup file created.

    :raises GWNotADirectoryError: if `overwrite` is not allowed and the
    backup file already exists.

    """
    backup_folder = Path(backup_folder or source_file.parent)
    if not backup_folder.exists():
        backup_folder.mkdir(parents=True, exist_ok=True)
    if simple_bak:
        backup_file = backup_folder / filename_variation(source_file.name, descriptor="", suffix=".bak")
    else:
        backup_file = backup_folder / filename_variation(source_file.name)
    if backup_file.exists() and not overwrite:
        raise GWNotADirectoryError(f"File {backup_file} already exists.")
    copy_file(str(source_file), str(backup_file))
    return backup_file


def md5_digest(target_file: Union[Path, str]):
    target_file = str(target_file)
    with open(target_file, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

