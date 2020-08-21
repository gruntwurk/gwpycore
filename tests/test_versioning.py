from gwpycore import version_numeric
from gwpycore import bump_version


def test_bump_version():
	assert bump_version("0.0.1") == "0.0.2"
	assert bump_version("2.0.0") == "2.0.1"
	assert bump_version("2.0.03") == "2.0.4"
	assert bump_version("2.0.13") == "2.0.14"
	assert bump_version("2 . 0 . 13") == "2.0.14"


def test_version_numeric():
	assert version_numeric("0.0.1") == [0,0,1]
	assert version_numeric("2.0.0") == [2,0,0]
	assert version_numeric("2.0.03") == [2,0,3]
	assert version_numeric("2.0.13") == [2,0,13]
	assert version_numeric("2 . 0 . 13") == [2,0,13]
