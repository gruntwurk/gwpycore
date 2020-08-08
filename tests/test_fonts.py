from ctypes import ArgumentError

import pytest

from gwpycore.gw_exceptions import GruntWurkArgumentError
from gwpycore.gw_fonts import (font_exists, full_font_name, install_font,
                               is_truetype)


def test_fontname():
    assert full_font_name("ariblk.ttf") == "Arial Black"
    assert full_font_name("arialbd.ttf") == "Arial Bold"
    assert full_font_name("SMALLE.FON") == "Small Fonts (VGA res)"


def test_is_truetype():
    assert is_truetype("ariblk.ttf")
    assert not is_truetype("SMALLE.FON")


def test_install_font_bad_type():
    with pytest.raises(GruntWurkArgumentError) as e_info:
        install_font("unknown_font_type.xxx")
    assert str(e_info.value) == 'Attempting to install "unknown_font_type.xxx", but only .otf and .ttf files can be installed.'


def test_install_font_exists_not():
    with pytest.raises(GruntWurkArgumentError) as e_info:
        install_font("no_such_font_file.ttf")
    assert str(e_info.value) == '"no_such_font_file.ttf" does not exist.'


def test_font_exists():
    assert font_exists("ariblk.ttf")
    assert not font_exists("no_such.ttf")
