"""
Functions:
    mkpath -- (same as in the deprecated distutils)
    copy_tree -- (same as in the deprecated distutils)
    remove_tree -- (same as in the deprecated distutils)
    copy_file -- (same as in the deprecated distutils)
    create_tree -- (same as in the deprecated distutils)
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
from distutils.errors import DistutilsFileError
import zipfile
from pathlib import Path
from typing import List, Union
import logging

from .exceptions import GWNotADirectoryError, GWFileExistsError
from .files import enquote_spaces, file_type_per_ext


__all__ = [
    "FileInventory",
    "itemize_folder",
    "mkpath",
    "copy_tree",
    "remove_tree",
    "create_tree",
    "zip_dir",
    "make_zip_backup",
]


LOG = logging.getLogger('gwpy')

# ############################################################################
# Since distutils.dir_util.* is deprecated...                  DIRECTORY UTILS
# ############################################################################


def mkpath(name, mode=0o777, verbose=0, dry_run=0) -> List:
    """
    Creates a directory and any missing ancestor directories.
    If the directory already exists (or if name is an empty string, which
    means the current directory, which of course exists), then this does nothing.

    :param name: Either a str or a Path.
    :param verbose: if true, prints a one-line summary of each mkdir to stdout.

    :return: A list of directories actually created.

    Side Effects:
        Writes to stdout.

    :raises: GWNotADirectoryError if unable to create some directory along the way
        (eg. some sub-path exists, but is a file rather than a directory).
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    try:
        return distutils.dir_util.mkpath(str(name), mode, verbose, dry_run)
    except DistutilsFileError as e:
        raise GWNotADirectoryError(e.message) from e


def create_tree(base_dir, files, mode=0o777, verbose=0, dry_run=0):
    """
    Creates all the empty directories under base_dir needed to put files there.

    Arguments:
        base_dir is just the name of a directory which doesn't necessarily exist yet.

        files is a list of filenames to be interpreted relative to base_dir.

        base_dir + the directory portion of every file in files will be created
        if it doesn't already exist.

        mode, verbose and dry_run flags are the same as for mkpath().
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    return distutils.dir_util.create_tree(str(base_dir), files, mode, verbose, dry_run)


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, update=0, verbose=0, dry_run=0):
    """
    Copies an entire directory tree `src` to a new location `dst`. The end
    result is that every file in `src` is copied to `dst`, and directories
    under `src` are recursively copied to `dst`.

    :param src: Must be a directory.

    :param dst: Must be a directory. If `dst` does not exist, it is created with
    mkpath().

    :param preserve_mode: If true (1, the default), each file's mode (type and
    permission bits, or whatever is analogous on the current platform) is
    copied. (Does not apply to the directories.)

    :param preserve_times: If true (1, the default), the last-modified and
    last-access times of each file are copied as well. (Does not apply to the
    directories.)

    :param preserve_symlinks: If true (1), symlinks will be copied as symlinks
    (on platforms that support them!); otherwise (the default), the file
    referenced by the symlink will be physically copied.

    :param update: Same as for copy_file().

    :param verbose:
    :param dry_run:

    :returns: the list of files that were copied (or might have been copied),
    using their output name. The return value is unaffected by `update` or
    `dry_run`. That is, it will simply be the list of all files under `src`,
    with the names changed to be under `dst`.

    :raises GWNotADirectoryError: if `src` is not a directory.
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    try:
        return distutils.dir_util.copy_tree(str(src), str(dst), preserve_mode, preserve_times, preserve_symlinks, update, verbose, dry_run)
    except DistutilsFileError as e:
        raise GWNotADirectoryError(e) from e


def remove_tree(directory, verbose=0, dry_run=0):
    """
    Recursively removes directory and all files and directories underneath it.

    Any errors are ignored (apart from being reported to sys.stdout if verbose
    is true).

    Side Effects:
        Writes to stdout.

    Returns:
        None
    """
    # FIXME Reimplement before 3.12 when distutils is permanently dropped
    return distutils.dir_util.remove_tree(str(directory), verbose, dry_run)


def make_zip_backup(source_folder, destination_folder, skip_hidden=False, hidden_chars=".", skip_folders=None):
    """
    Zips up the specified folder.

    :param source_folder: The folder to be backed up.
    :param destination_folder: Where to place the zip file.
    :param skip_hidden: Whether or not to skip hidden files/folders, defaults to False.
    :param hidden_chars: How hidden files/folders are specified (by their
        leading character), defaults to ".". Multiple starting characters can
        be given.
    :param skip_folders: A specific list of folders to skip, defaults to None.
    """
    source_folder = Path(source_folder)
    destination_folder = Path(destination_folder)
    subdir = source_folder.name
    source_folder = source_folder.parent
    if skip_folders is None:
        skip_folders = []
    zip_file = destination_folder / f'{subdir}.zip'
    if zip_file.exists() and zip_file.stat().st_size > 0:
        raise GWFileExistsError(f"WARNING Backup skipped -- {zip_file} already exists.")
    contents = itemize_folder(source_folder / subdir, skip_hidden=skip_hidden, hidden_chars=hidden_chars, skip_folders=skip_folders)
    zip_dir(zip_file, source_folder / subdir, contents)


def itemize_folder(folder: Path, base_folder: Path = None, callback=None, skip_hidden=False, hidden_chars=".",
                   skip_extensions=[], skip_folders=[]) -> List[str]:
    """
    A simple recursive listing of the contents of a directory with the ability
    to filter out files/dirs in various ways.

    See also the `FileInventory` class for a more advanced alternative to
    this function.

    :param folder: The root folder to search recursively.

    :param base_folder: An alternate folder to base the relativity on (defaults to the same as `folder`).

    :param callback: A callback function that contains custom filter logic.
    It should takes one argument (a Path element) and return a bool (True for
    include, False for exclude). Defaults to None.

    :param skip_hidden: Whether or not to skip files/subfolders that begin with
    certain character(s). Defaults to False.

    :param hidden_chars: What prefix character(s) make a file/folder "hidden."
    Defaults to "."

    :param skip_extensions: Which file extension(s) (suffixes), if any, are to
    be skipped as well. Defaults to [].

    :return: A list of strs representing the discovered files (the str being
    the relative path and filename -- relative to `base_folder`).
    """
    if not base_folder:
        base_folder = folder

    def should_include(element: Path) -> bool:
        if skip_hidden and element.name[0] in hidden_chars:
            return False
        if element.is_file():
            if skip_extensions and element.suffix in skip_extensions:
                return False
        elif element.is_dir():
            if skip_folders and element.name in skip_folders:
                return False
        return callback(element) if callback else True

    def recurse_folder(filenames, folder: Path):
        elements = folder.glob('*')
        for element in elements:
            if should_include(element):
                if element.is_file():
                    filenames.append(str(element.relative_to(base_folder)))
                elif element.is_dir():
                    recurse_folder(filenames, element)

    filenames = []
    recurse_folder(filenames, folder)
    return filenames


def zip_dir(zip_filespec: Union[Path, str], root_dir: Union[Path, str], relative_contents: List[str]):
    root_dir = Path(root_dir)
    with zipfile.ZipFile(zip_filespec, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in relative_contents:
            try:
                zipf.write(root_dir / item, item)
            except ValueError as e:
                LOG.warning(f'Error attempting to ZIP {item}: {str(e)}')


# ############################################################################
#                                                          FILEINVENTORY CLASS
# ############################################################################

class FileInfo():
    """
    Used by FileInventory.
    base_path: Used to determine the relative path for the folder_name field.
    """

    def __init__(self, file_path: Path, base_path: Path) -> None:
        self._file_path = file_path
        self._file_size = self._file_path.stat().st_size
        self._folder_name = str(file_path.parent.relative_to(base_path))
        self._file_name = self.file_path.name

    @property
    def file_path(self):
        """The full file Path, as given (read only)."""
        return self._file_path

    @property
    def file_size(self):
        """Same as file_path.stat().st_size (read only)."""
        return self._file_size

    @property
    def folder_name(self):
        """The sub-folder path, relative to the given base path (read only)."""
        return self._folder_name

    @property
    def file_name(self):
        """The file name with any extension, but no path (read only)."""
        return self._file_name

    @property
    def file_type(self):
        """The file extension (sans dot and converted to lower case; read only)."""
        return file_type_per_ext(self.file_path)

    def quick_digest(self) -> str:
        """
        This simply returns the file type and the file size as a concatenated
        string. Comparing this quick digest to that of another file is an
        expedient way to rule out if one is a copy of the other. This cuts way
        down on having to take the time to compute a real message digest.
        """
        return self.file_type + str(self.file_size).zfill(8)


class FileInventory():
    """
    Analyzes the contents of a directory tree.
    Looks for duplicate files, etc.

    See also the `itemize_folder` function for a simpler alternative to this class.

    :param exclude_paths: a list of str of subfolders to exclude (relative to the base path).
    :param exclude_types: a list of str of file types (extensions) to exclude.
    """

    def __init__(self, base_path_str: str, exclude_paths=None, exclude_types=None) -> None:
        if exclude_paths is None:
            exclude_paths = []
        if exclude_types is None:
            exclude_types = []
        self._folder_names = []
        self._file_info = []
        self.base_path = Path(base_path_str)
        self.exclude_paths = [p.casefold() for p in exclude_paths]
        self.exclude_types = [file_type_per_ext(t) for t in exclude_types]

    @property
    def folder_names(self):
        """The folder_names property."""
        return self._folder_names

    @property
    def file_info(self):
        """The file_info property."""
        return self._file_info

    def analyze(self):
        """
        Builds a list of folder names (list of strings).
        Builds a list of files (list of FileInfo objects).
        """
        self._folder_names = []
        self._file_info = []
        self._itemize_folder(self.base_path)

    def _itemize_folder(self, folder: Path):
        """Load the info of a single subfolder. Is called recursively."""
        elements = folder.glob('*')
        for element in elements:
            if element.is_dir():
                parent = str(element.relative_to(self.base_path))
                if parent.casefold() in self.exclude_paths:
                    continue
                self.folder_names.append(parent)
                self._itemize_folder(element)
            elif element.is_file():
                info = FileInfo(element, self.base_path)
                if info.file_type in self.exclude_types:
                    continue
                self.file_info.append(info)

    def compare_folders(self, reference_inventory: "FileInventory", mkdir_cmd="mkdir") -> List:
        """
        Returns a list of mkdir commands for every folder that exists in the
        reference inventory but does not exist in this inventory.
        """
        return [
            f"{mkdir_cmd} {folder_name}"
            for folder_name in reference_inventory.folder_names
            if folder_name not in self.folder_names
        ]

    def files_by_name(self):
        """
        Returns a hash table of the FileInfo objects, keyed by the file name.
        "Hash table" meaning a dict that contains lists.
        """
        results = {}
        for info in self.file_info:
            if info.file_name in results:
                results[info.file_name].append(info)
            results[info.file_name] = [info]
        return results

    # Since this class is type-hinting itself, the name has to be quoted.
    def compare_files(self, reference_inventory: "FileInventory", move_cmd="mv") -> List:
        """
        Returns a list of move commands for every file that exists in both this
        inventory and the reference inventory (by name), but in a different folder.
        Note: for Windows, use move_cmd="move /Y"
        """
        shell_commands = []
        existing_files = self.files_by_name()
        target_files = reference_inventory.files_by_name()
        for target in reference_inventory.file_info:
            if target.file_name not in existing_files:
                continue
            sources = existing_files[target.file_name]
            for source in sources:
                if source.folder_name == target.folder_name:
                    continue
                if source.file_name in target_files:
                    continue
                file_in_current_location = enquote_spaces(source.folder_name.replace("/", "\\") + "\\" + source.file_name)
                destination_folder = enquote_spaces(target.folder_name.replace("/", "\\"))
                shell_commands.append(f"{move_cmd} {file_in_current_location} {destination_folder}")
        return shell_commands

    def add_files(self, reference_inventory: "FileInventory", copy_cmd="cp") -> List:
        """
        Returns a list of copy commands for every file that exists in
        the reference inventory, but not in this inventory.
        """
        shell_commands = []
        existing_files = self.files_by_name()
        for source in reference_inventory.file_info:
            if source.file_name not in existing_files:
                file_in_current_location = enquote_spaces(
                    (str(reference_inventory.base_path) + "\\" + source.folder_name).replace("/", "\\") + "\\" + source.file_name
                )
                destination_folder = enquote_spaces(source.folder_name.replace("/", "\\"))
                shell_commands.append(f"{copy_cmd} {file_in_current_location} {destination_folder}")
        return shell_commands
