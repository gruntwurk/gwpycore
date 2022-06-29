# This Python 3 Windows font installer code is copyrighted(C) 2017 Lahiru
# Pathirage <lpsandaruwan@gmail.com> 20/02/17 and provided with the ability
# to redistribute and/or modify per the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version <http://www.gnu.org/licenses/>.

# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import ctypes
import os
import shutil
import sys
from ctypes import wintypes
from pathlib import Path

from ..gw_basis.gw_exceptions import EX_ERROR, EX_OK, GruntWurkValueError

try:
    import winreg
except ImportError:
    import _winreg as winreg


class WindowsFontInstaller:
    """
    A utility class (short-lived) for installing fonts (TTF or OTF) into MS Windows.
    IMPORTANT: Requires system priveledges.
    This will install the font and inform programs that a new font has been added.

    arguments:
        font_filename -- The name and path of the font file, including the
            .ttf or .otf extension. It must be one specific file, no wildcards.

    example:
        with WindowsFontInstaller("fancy_font.ttf") as installer:
            if not installer.font_exists():
                try:
                    installer.install_font()
                    print(f"Installed {installer.full_font_name()} ({installer.font_filename})."
                except GruntWurkValueError, WindowsError as e:
                    pass

    """

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

    FONTS_REG_PATH = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"

    HWND_BROADCAST = 0xFFFF
    SMTO_ABORTIFHUNG = 0x0002
    WM_FONTCHANGE = 0x001D
    GFRI_DESCRIPTION = 1
    GFRI_ISTRUETYPE = 3

    if not hasattr(wintypes, "LPDWORD"):
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

    user32.SendMessageTimeoutW.restype = wintypes.LPVOID
    # hWnd  # Msg  # wParam  # lParam  # fuFlags  # uTimeout  # lpdwResult
    user32.SendMessageTimeoutW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.LPVOID, wintypes.LPVOID, wintypes.UINT, wintypes.UINT, wintypes.LPVOID)

    gdi32.AddFontResourceW.argtypes = (wintypes.LPCWSTR,)  # lpszFilename

    # http://www.undocprint.org/winspool/getfontresourceinfo
    # lpszFilename  # cbBuffer  # lpBuffer  # dwQueryType
    gdi32.GetFontResourceInfoW.argtypes = (wintypes.LPCWSTR, wintypes.LPDWORD, wintypes.LPVOID, wintypes.DWORD)

    def __init__(self, font_filename):
        self.font_filename = font_filename
        self.font_path = Path(self.font_filename)

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def font_exists(self) -> bool:
        """
        Determines if the font has already been installed.
        """
        cb = wintypes.DWORD()
        if self.gdi32.GetFontResourceInfoW(self.font_filename, ctypes.byref(cb), None, self.GFRI_DESCRIPTION):
            return True
        return False

    def is_truetype(self) -> bool:
        """
        Determines if the installed font is a TrueType font.
        """
        is_tt = wintypes.BOOL()
        cb = wintypes.DWORD()
        cb.value = ctypes.sizeof(is_tt)
        self.gdi32.GetFontResourceInfoW(self.font_path.name, ctypes.byref(cb), ctypes.byref(is_tt), self.GFRI_ISTRUETYPE)
        return bool(is_tt)

    def full_font_name(self) -> str:
        """
        Determines (as best as we can) the full font name for the installed font.

        For example:
            assert WindowsFontInstaller.("arialbd.ttf").full_font_name() == "Arial Bold"
            assert WindowsFontInstaller.("SMALLE.FON").full_font_name() == "Small Fonts (VGA res)"
            assert WindowsFontInstaller.("no-such-font.ttf").full_font_name() == "no-such-font"
        """
        # Strip off the extension to get the default fontname...
        fontname = os.path.splitext(self.font_filename)[0]

        cb = wintypes.DWORD()
        if self.gdi32.GetFontResourceInfoW(self.font_filename, ctypes.byref(cb), None, self.GFRI_DESCRIPTION):
            buf = (ctypes.c_wchar * cb.value)()
            if self.gdi32.GetFontResourceInfoW(self.font_filename, ctypes.byref(cb), buf, self.GFRI_DESCRIPTION):
                fontname = buf.value

        return fontname

    def install_font(self):
        """
        Installs the font.
        Raises a GruntWurkValueError or WindowsError exception if unsuccessful.
        """
        if not (self.font_path.suffix.lower() in [".otf", ".ttf"]):
            raise GruntWurkValueError(f"Attempting to install '{self.font_filename}', but only .otf and .ttf files can be installed.")
        if not (self.font_path.exists()):
            raise GruntWurkValueError(f"'{self.font_filename}' does not exist.")

        filename_alone = self.font_path.name
        windows_font_path = Path(os.environ["SystemRoot"]) / "Fonts" / filename_alone

        shutil.copy(self.font_filename, windows_font_path)

        # load the font in the current session
        if not self.gdi32.AddFontResourceW(windows_font_path):
            windows_font_path.unlink()
            raise WindowsError(f"AddFontResource failed to load '{self.font_filename}'")

        # notify running programs that there's been a font change
        self.user32.SendMessageTimeoutW(self.HWND_BROADCAST, self.WM_FONTCHANGE, 0, 0, self.SMTO_ABORTIFHUNG, 1000, None)

        font_name = self.full_font_name()
        if self.is_truetype():
            font_name += " (TrueType)"

        # store the fontname/filename in the registry (to survive the next reboot)
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, filename_alone)


def do_font_exists(argv):
    """
    Entry point for the font_exists script. (See setup.py)
    Checks that all of the fonts named on the command-line exist.
    Exits with code 0 (OK) if they all exit, or 2 (EX_ERROR) if any one of
    them does not.
    """
    for arg in argv[1:]:
        with WindowsFontInstaller(arg) as installer:
            if not installer.font_exists():
                sys.exit(EX_ERROR)
    sys.exit(EX_OK)


def do_install_font(argv):
    """
    Entry point for the install_font script. (See setup.py)
    Installs all of the fonts named in the command-line (specific arguments,
    no wildcards).
    Exits with code 0 (OK) if the installs were successful, or a positive
    error code if not.
    """
    for arg in argv[1:]:
        print("Installing " + arg)
        try:
            with WindowsFontInstaller(arg) as installer:
                installer.install_font()
        except GruntWurkValueError as e:
            print(e.message)
            sys.exit(e.exitcode)
    sys.exit(0)


if __name__ == "__main__":
    do_install_font(sys.argv)

__all__ = ("do_font_exists", "do_install_font", "WindowsFontInstaller")
