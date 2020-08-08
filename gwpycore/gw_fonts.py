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
from gwpycore.gw_exceptions import EX_OK, EX_ERROR, GruntWurkArgumentError
import os
import shutil
import sys
from pathlib import Path

from ctypes import ArgumentError, wintypes

try:
    import winreg
except ImportError:
    import _winreg as winreg

user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

HWND_BROADCAST = 0xFFFF
SMTO_ABORTIFHUNG = 0x0002
WM_FONTCHANGE = 0x001D
GFRI_DESCRIPTION = 1
GFRI_ISTRUETYPE = 3

if not hasattr(wintypes, 'LPDWORD'):
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

user32.SendMessageTimeoutW.restype = wintypes.LPVOID
user32.SendMessageTimeoutW.argtypes = (
    wintypes.HWND,   # hWnd
    wintypes.UINT,   # Msg
    wintypes.LPVOID,  # wParam
    wintypes.LPVOID,  # lParam
    wintypes.UINT,   # fuFlags
    wintypes.UINT,   # uTimeout
    wintypes.LPVOID  # lpdwResult
)

gdi32.AddFontResourceW.argtypes = (
    wintypes.LPCWSTR,)  # lpszFilename

# http://www.undocprint.org/winspool/getfontresourceinfo
gdi32.GetFontResourceInfoW.argtypes = (
    wintypes.LPCWSTR,  # lpszFilename
    wintypes.LPDWORD,  # cbBuffer
    wintypes.LPVOID,  # lpBuffer
    wintypes.DWORD)   # dwQueryType


def font_exists(filename) -> bool:
    """
    Determine if a font (based on the filename of the font) has been installed.

    For example:

        assert font_exists("ariblk.ttf")
        assert not font_exists("no_such.ttf")
    """
    cb = wintypes.DWORD()
    if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None, GFRI_DESCRIPTION):
        return True
    return False

def is_truetype(filename) -> bool:
    """
    Determine if an installed font (based on the filename of the font) is a TrueType font.

    For example:

        assert is_truetype("ariblk.ttf")
        assert not is_truetype("SMALLE.FON")
    """
    is_tt = wintypes.BOOL()
    cb = wintypes.DWORD()
    cb.value = ctypes.sizeof(is_tt)
    gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), ctypes.byref(is_tt), GFRI_ISTRUETYPE)
    return bool(is_tt)

def full_font_name(filename) -> str:
    """
    Determine (as best as we can) the full font name for an installed font
    based on the filename of the font.

    For example:

        assert full_font_name("arialbd.ttf") == "Arial Bold"
        assert full_font_name("SMALLE.FON") == "Small Fonts (VGA res)"
        assert full_font_name("no-such-font.ttf") == "no-such-font"
    """
    # Strip off the extension to get the default fontname...
    fontname = os.path.splitext(filename)[0]

    cb = wintypes.DWORD()
    if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None, GFRI_DESCRIPTION):
        buf = (ctypes.c_wchar * cb.value)()
        if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), buf, GFRI_DESCRIPTION):
            fontname = buf.value

    return fontname

def install_font(font_filename):
    """
    Installs a TTF or OTF font into Windows.
    IMPORTANT: Requires system priveledges.
    This will install the font and inform programs that a new font has been added.

    arguments:
        font_filename -- The name and path of the font file, including the .ttf or .otf extension.
                    It must be one specific file, no wildcards.
    """
    font_path = Path(font_filename)
    if not (font_path.suffix.lower() in ['.otf', '.ttf']):
        raise GruntWurkArgumentError(f'Attempting to install "{font_filename}", but only .otf and .ttf files can be installed.')
    if not (font_path.exists()):
        raise GruntWurkArgumentError(f'"{font_filename}" does not exist.')

    filename_alone = font_path.name
    windows_font_path = Path(os.environ['SystemRoot']) / 'Fonts' / filename_alone

    shutil.copy(font_filename, windows_font_path)

    # load the font in the current session
    if not gdi32.AddFontResourceW(windows_font_path):
        windows_font_path.unlink()
        raise WindowsError(f'AddFontResource failed to load "{font_filename}"')

    # notify running programs that there's been a font change
    user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None
    )

    font_name = full_font_name(filename_alone)
    if is_truetype(filename_alone):
        font_name += ' (TrueType)'

    # store the fontname/filename in the registry (to survive the next reboot)
    with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, filename_alone)


def do_font_exists(argv):
    """
    Entry point for the font_exists script. (See setup.py)
    Only checks the first command-line argument. Others are ignored.
    Exits with code 0 (OK) if the font does exists, or 2 (EX_ERROR) if not.
    """
    arg = argv[1]
    sys.exit(EX_OK if font_exists(arg) else EX_ERROR)

def do_install_font(argv):
    """
    Entry point for the install_font script. (See setup.py)
    Installs all of the fonts named in the command-line (specific arguments, no wildcards).
    Exits with code 0 (OK) if the installs were successful, or a positiove error code if not.
    """
    for arg in argv[1:]:
        print('Installing ' + arg)
        try:
            install_font(arg)
        except GruntWurkArgumentError as e:
            print(e.message)
            sys.exit(e.exitcode)
    sys.exit(0)


if __name__ == '__main__':
    do_install_font(sys.argv)

__all__ = ("install_font", "is_truetype", "full_font_name")
