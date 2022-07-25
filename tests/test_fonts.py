import pytest

from gwpycore import GWValueError
from gwpycore.windows import WindowsFontInstaller


def test_fontname():
    assert WindowsFontInstaller("ariblk.ttf").full_font_name() == "Arial Black"
    assert WindowsFontInstaller("arialbd.ttf").full_font_name() == "Arial Bold"
    assert WindowsFontInstaller("SMALLE.FON").full_font_name() == "Small Fonts (VGA res)"


def test_is_truetype():
    assert WindowsFontInstaller("ariblk.ttf").is_truetype()
    assert not WindowsFontInstaller("SMALLE.FON").is_truetype()


def test_install_font_bad_type():
    with pytest.raises(GWValueError) as e_info:
        WindowsFontInstaller("unknown_font_type.xxx").install_font()
    assert str(e_info.value) == "Attempting to install 'unknown_font_type.xxx', but only .otf and .ttf files can be installed."


def test_install_font_exists_not():
    with pytest.raises(GWValueError) as e_info:
        WindowsFontInstaller("no_such_font_file.ttf").install_font()
    assert str(e_info.value) == "'no_such_font_file.ttf' does not exist."


def test_font_exists():
    assert WindowsFontInstaller("ariblk.ttf").font_exists()
    assert not WindowsFontInstaller("no_such.ttf").font_exists()
