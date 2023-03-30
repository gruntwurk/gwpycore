from pathlib import Path
import shutil

from ..core.config import GlobalSettings
from ..core.exceptions import GWFileNotFoundError

__all__ = [
    'check_first_time_install',
]

CONFIG = GlobalSettings()


def check_first_time_install(local_folder_name='local', local_default_name='local_default', flag_file_name='first_time_install.txt'):
    """
    Sets `CONFIG.first_time_install` to whether or not this is the first time
    that the application is being executed -- according to whether or not a
    certain flag file exists in the application folder. (If so, the flag file
    is deleted.)

    Either way, it also checks that a local-settings folder exixts, creating
    it if needed, and populating it from a defaults folder.

    :param local_folder_name: The name of the local-settings folder, relative
        to the application folder. Defaults to `local`.

    :param local_default_name: The name of the folder that contains the default
        settings files to be used to initialze a first-time setup, relative
        to the application folder. Defaults to `local_default`.

    :param flag_file_name: The name of the flag file to look for that indicates
        if this is a first time install. Defaults to `first_time_install.txt`.

    :raises GWFileNotFoundError: If either the local folder, or the local
        defaults folder are missing when it's expected to exist.
    """
    flag_file = Path(flag_file_name)
    if is_first_time := flag_file.exists():
        flag_file.unlink()
    CONFIG.first_time_install = is_first_time

    local_folder = Path(local_folder_name)
    if local_folder.exists():
        return
    if not is_first_time:
        raise GWFileNotFoundError(f'The "{local_folder_name}" folder is missing, yet this is not a first-time install.')

    local_default = Path(local_default_name)
    if not local_default.exists():
        raise GWFileNotFoundError(f'The "{local_default_name}" folder is missing, so there is nothing from which to initialize the "{local_folder_name}" folder.')

    local_folder.mkdir()
    shutil.copytree(local_default_name, local_folder_name)
