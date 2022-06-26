"""
Functions:
    enquote_spaces(file_name)
    file_type_per_ext(filespec)
    filename_variation(filespec, variation_descriptor)
    save_backup_file(source_file, backup_folder)
Classes:
    FileInventory -- Analyzes the contents of a directory tree.
        Looks for duplicate files, etc.
    FileInfo -- Used by FileInventory
For Reference:
    Path(filespec).touch()
"""
import shutil
from pathlib import Path
from typing import List, Union
from .gw_datetime import timestamp

MAX_HEIGHT = 1200
MAX_WIDTH = 1920
TEMP_FILE = '_temp.jpg'


def enquote_spaces(file_name: str) -> str:
    """
    Returns the given file name. If the name contains one or more spaces, then
    the name is first enclosed in double-quotes.
    """
    if " " in file_name:
        return f'"{file_name}"'
    return file_name


def file_type_per_ext(filespec: Union[Path, str]) -> str:
    """
    Returns the file type based on a file name's extension (sans dot and
    converted to lower case).

    filespec: Either a Path, a string that names a file, or a string with just
        a file extension (leading dot).
    """
    return Path(filespec).suffix.casefold().replace(".", "")


def filename_variation(filespec, variation_descriptor=timestamp()) -> str:
    """
    Given the name (or Path) of an original file, this returns a corresponding
    filename that includes the variation_descriptor. If no variation_descriptor
    is specified, then a timestamp will be used.
    """
    if type(filespec) is str:
        filespec = Path(filespec)
    return str(filespec.with_name(filespec.stem + "_" + str(variation_descriptor) + filespec.suffix))


def save_backup_file(source_file: Path, backup_folder: Path):
    """
    Makes a copy of the source file in the backup folder while adding a
    timestamp to the name of the backup copy.

    Throws: OSError, shutil.SameFileError
    """
    if not backup_folder.exists():
        backup_folder.mkdir(parents=True, exist_ok=True)
    backup_file = Path(backup_folder) / filename_variation(source_file.name)
    shutil.copy(str(source_file), str(backup_file))



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

    exclude_paths: a list of str of subfolders to exclude (relative to the base path).
    exclude_types: a list of str of file types (extensions) to exclude.
    """

    def __init__(self, base_path_str: str, exclude_paths=[], exclude_types=[]) -> None:
        self._folder_names = []
        self._file_info = []
        self.base_path = Path(base_path_str)
        self.exclude_paths = [p.casefold() for p in exclude_paths]
        self.exclude_types = [file_type_per_ext(t) for t in exclude_types]

    @property
    def folder_names(self):
        """The folder_names property."""
        return self._folder_names
    @folder_names.setter
    def folder_names(self, value):
        self._folder_names = value
    @property
    def file_info(self):
        """The file_info property."""
        return self._file_info

    def analyze(self):
        """
        Builds a list of folder names (list of strings).
        Builds a list of files (list of FileInfo objects).
        """
        self.folder_names = []
        self.file_info = []
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
        shell_commands = []
        for folder_name in reference_inventory.folder_names:
            if folder_name not in self.folder_names:
                shell_commands.append(f"{mkdir_cmd} {folder_name}")
        return shell_commands

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
                file_in_current_location = enquote_spaces((str(reference_inventory.base_path) + "\\" +
                                                           source.folder_name).replace("/", "\\") + "\\" + source.file_name)
                destination_folder = enquote_spaces(source.folder_name.replace("/", "\\"))
                shell_commands.append(f"{copy_cmd} {file_in_current_location} {destination_folder}")
        return shell_commands


__all__ = ["FileInventory", "enquote_spaces", "file_type_per_ext", "filename_variation", "save_backup_file"]
