from gwpycore import file_type_per_ext, filename_variation


def test_file_type_per_ext():
    assert file_type_per_ext("image.jpg") == "jpg"
    assert file_type_per_ext("image.png") == "png"
    assert file_type_per_ext("path/image.png") == "png"
    assert file_type_per_ext("path\\image.png") == "png"
    assert file_type_per_ext("C:path\\image.png") == "png"
    assert file_type_per_ext("C:path\\subpath\\image.png") == "png"


def test_filename_variation():
    assert filename_variation("image.jpg", "128") == "image_128.jpg"
    assert filename_variation("image.jpg", "150") == "image_150.jpg"
    assert filename_variation("path/image.jpg","128") == "path\\image_128.jpg"
    assert filename_variation("path\\image.jpg", "225") == "path\\image_225.jpg"
