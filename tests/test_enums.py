from enum import unique, Enum
from gwpycore import enum_by_name


@unique
class SampleEnum(Enum):
    single_string = 'bar'
    string_with_extra = ('bar', 'The bar in "foo bar baz"')
    SINGLE_INT = 17
    single_RGB = (128, 0, 128)
    single_RGBA = (210, 96, 0, 128)
    RGB_with_extra = ((128, 0, 128), 'Magenta')
    RGBA_with_extra = ((210, 96, 0, 128), 'Orangish', 'Translucent')


def test_enum_by_name():
    assert enum_by_name(SampleEnum, 'single_string') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'SINGLE_STRING') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'Single_String') == SampleEnum.single_string
    assert enum_by_name(SampleEnum, 'RGBA_with_extra') == SampleEnum.RGBA_with_extra
    assert enum_by_name(SampleEnum, 'no_such') is None
    assert enum_by_name(SampleEnum, None) is None
    assert enum_by_name(SampleEnum, '') is None
