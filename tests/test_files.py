from gwpycore import file_type_per_ext


def test_image_tools_file_type_per_ext():
    assert file_type_per_ext("image.jpg") == "jpg"
    assert file_type_per_ext("image.png") == "png"
    assert file_type_per_ext("path/image.png") == "png"
    assert file_type_per_ext("path\\image.png") == "png"
    assert file_type_per_ext("C:path\\image.png") == "png"
    assert file_type_per_ext("C:path\\subpath\\image.png") == "png"

