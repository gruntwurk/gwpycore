import pytest
from enum import unique, Enum
from gwpycore import (GWEnum, enum_by_name)
from gwpycore.core.enums import enum_by_value


@unique
class SampleEnum(Enum):
    single_string = 'bar'
    string_with_extra = ('bar', 'The bar in "foo bar baz"')
    SINGLE_INT = 17
    single_RGB = (128, 0, 128)
    single_RGBA = (210, 96, 0, 128)
    RGB_with_extra = ((128, 0, 128), 'Magenta')
    RGBA_with_extra = ((210, 96, 0, 128), 'Orangish', 'Translucent')


@unique
class PluralValues(GWEnum):
    string_with_extra = ('bar', 'The bar in "foo bar baz"')
    INT_WITHOUT_EXTRA = 17
    RGB_with_extra = ((128, 0, 128), 'Magenta')
    RGBA_with_extra = ((210, 96, 0, 128), 'Orangish', 'Translucent')
    # The base implementation of `GWEnum.value_count` returns the len() of the
    # value if the value is a tuple or list.

@unique
class SingularValue(GWEnum):
    single_string = 'bar'
    SINGLE_INT = 17
    single_RGB = (128, 0, 128)
    single_RGBA = (210, 96, 0, 128)

    # Override the base implementation of `GWEnum.value_count` to force the
    # value to be treated as a single value, even if it's a tuple or list.
    def value_count(self) -> int:
        return 1


def test_enum_by_name():
    assert enum_by_name(SampleEnum, 'single_string') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'SINGLE_STRING') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'Single_String') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'RGBA_with_extra') == SampleEnum.RGBA_with_extra
    assert enum_by_name(SampleEnum, 'no_such') is None
    assert enum_by_name(SampleEnum, None) is None
    assert enum_by_name(SampleEnum, '') is None


def test_value_count():
    assert PluralValues.string_with_extra.value_count() == 2
    assert PluralValues.INT_WITHOUT_EXTRA.value_count() == 1
    assert PluralValues.RGB_with_extra.value_count() == 2
    assert PluralValues.RGBA_with_extra.value_count() == 3
    assert SingularValue.single_string.value_count() == 1
    assert SingularValue.SINGLE_INT.value_count() == 1
    assert SingularValue.single_RGB.value_count() == 1
    assert SingularValue.single_RGBA.value_count() == 1


def test_primary_value():
    assert PluralValues.string_with_extra.primary_value() == 'bar'
    assert PluralValues.INT_WITHOUT_EXTRA.primary_value() == 17
    assert PluralValues.RGB_with_extra.primary_value() == (128, 0, 128)
    assert PluralValues.RGBA_with_extra.primary_value() == (210, 96, 0, 128)
    assert SingularValue.single_string.primary_value() == 'bar'
    assert SingularValue.SINGLE_INT.primary_value() == 17
    assert SingularValue.single_RGB.primary_value() == (128, 0, 128)
    assert SingularValue.single_RGBA.primary_value() == (210, 96, 0, 128)


def test_secondary_value_singular():
    assert PluralValues.string_with_extra.secondary_value() == 'The bar in "foo bar baz"'
    assert PluralValues.INT_WITHOUT_EXTRA.secondary_value() is None
    assert PluralValues.RGB_with_extra.secondary_value() == 'Magenta'
    assert PluralValues.RGBA_with_extra.secondary_value() == 'Orangish'
    assert SingularValue.single_string.secondary_value() is None
    assert SingularValue.SINGLE_INT.secondary_value() is None
    assert SingularValue.single_RGB.secondary_value() is None
    assert SingularValue.single_RGBA.secondary_value() is None


def test_secondary_values_plural():
    assert PluralValues.string_with_extra.secondary_values() == ('The bar in "foo bar baz"', )
    assert PluralValues.INT_WITHOUT_EXTRA.secondary_values() is None
    assert PluralValues.RGB_with_extra.secondary_values() == ('Magenta', )
    assert PluralValues.RGBA_with_extra.secondary_values() == ('Orangish', 'Translucent')
    assert SingularValue.single_string.secondary_values() is None
    assert SingularValue.SINGLE_INT.secondary_values() is None
    assert SingularValue.single_RGB.secondary_values() is None
    assert SingularValue.single_RGBA.secondary_values() is None


def test_display_name():
    assert PluralValues.string_with_extra.display_name() == 'bar'
    assert PluralValues.INT_WITHOUT_EXTRA.display_name() == 'INT_WITHOUT_EXTRA'
    assert PluralValues.RGB_with_extra.display_name() == 'RGB_with_extra'
    assert PluralValues.RGBA_with_extra.display_name() == 'RGBA_with_extra'
    assert SingularValue.single_string.display_name() == 'bar'
    assert SingularValue.SINGLE_INT.display_name() == 'SINGLE_INT'
    assert SingularValue.single_RGB.display_name() == 'single_RGB'
    assert SingularValue.single_RGBA.display_name() == 'single_RGBA'

    assert PluralValues.string_with_extra.description() == 'bar'
    assert PluralValues.INT_WITHOUT_EXTRA.description() == 'INT_WITHOUT_EXTRA'
    assert PluralValues.RGB_with_extra.description() == 'RGB_with_extra'
    assert PluralValues.RGBA_with_extra.description() == 'RGBA_with_extra'
    assert SingularValue.single_string.description() == 'bar'
    assert SingularValue.SINGLE_INT.description() == 'SINGLE_INT'
    assert SingularValue.single_RGB.description() == 'single_RGB'
    assert SingularValue.single_RGBA.description() == 'single_RGBA'


def test_possible_values():
    assert PluralValues.possible_values() == ['bar', 'INT_WITHOUT_EXTRA', 'RGB_with_extra', 'RGBA_with_extra']
    assert SingularValue.possible_values() == ['bar', 'SINGLE_INT', 'single_RGB', 'single_RGBA']


def test_by_name():
    assert PluralValues.by_name('string_with_extra') == PluralValues.string_with_extra
    assert PluralValues.by_name('RGB_with_extra') == PluralValues.RGB_with_extra
    assert PluralValues.by_name('RGBA_with_extra') == PluralValues.RGBA_with_extra
    assert SingularValue.by_name('SINGLE_INT') == SingularValue.SINGLE_INT
    assert SingularValue.by_name('single_RGB') == SingularValue.single_RGB
    assert SingularValue.by_name('single_RGBA') == SingularValue.single_RGBA

    assert SingularValue.by_name('single_string') == SingularValue.single_string
    assert SingularValue.by_name('    single_string') == SingularValue.single_string
    assert SingularValue.by_name('Single_string!!!') == SingularValue.single_string
    assert SingularValue.by_name('Single_String') == SingularValue.single_string
    assert SingularValue.by_name('SINGLE_STRING') == SingularValue.single_string

    assert PluralValues.by_name('INT_WITHOUT_EXTRA') == PluralValues.INT_WITHOUT_EXTRA
    assert PluralValues.by_name('int_without_extra') == PluralValues.INT_WITHOUT_EXTRA
    assert PluralValues.by_name('Int_Without_Extra') == PluralValues.INT_WITHOUT_EXTRA


def test_by_value():
    assert PluralValues.by_value(None) == PluralValues.string_with_extra  # default
    assert PluralValues.by_value("") == PluralValues.string_with_extra  # default
    assert PluralValues.by_value('bar') == PluralValues.string_with_extra
    assert PluralValues.by_value('INT_WITHOUT_EXTRA') == PluralValues.INT_WITHOUT_EXTRA
    assert PluralValues.by_value('RGB_with_extra') == PluralValues.RGB_with_extra
    assert PluralValues.by_value('RGBA_with_extra') == PluralValues.RGBA_with_extra
    assert SingularValue.by_value('bar') == SingularValue.single_string
    assert SingularValue.by_value('SINGLE_INT') == SingularValue.SINGLE_INT
    assert SingularValue.by_value('single_RGB') == SingularValue.single_RGB
    assert SingularValue.by_value('single_RGBA') == SingularValue.single_RGBA
    with pytest.raises(ValueError) as e_info:
        _ = SingularValue.by_value('no_such')
        assert e_info == "No such PluralValues with a primary value of no_such"


def test_default():
    assert PluralValues.default() == PluralValues.string_with_extra
    assert SingularValue.default() == SingularValue.single_string


def test_enum_by_value():
    assert enum_by_value(PluralValues, None) is None
    assert enum_by_value(PluralValues, "") is None
    assert enum_by_value(PluralValues, 0) is None
    assert enum_by_value(PluralValues, 27) is None  # not a string
    assert enum_by_value(PluralValues, 'bar') == PluralValues.string_with_extra
    assert enum_by_value(PluralValues, 'INT_WITHOUT_EXTRA') == PluralValues.INT_WITHOUT_EXTRA
    assert enum_by_value(PluralValues, 'RGB_with_extra') == PluralValues.RGB_with_extra
    assert enum_by_value(PluralValues, 'RGBA_with_extra') == PluralValues.RGBA_with_extra
    assert enum_by_value(SingularValue, 'bar') == SingularValue.single_string
    assert enum_by_value(SingularValue, 'SINGLE_INT') == SingularValue.SINGLE_INT
    assert enum_by_value(SingularValue, 'single_RGB') == SingularValue.single_RGB
    assert enum_by_value(SingularValue, 'single_RGBA') == SingularValue.single_RGBA
