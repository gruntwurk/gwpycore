# pip install dlib
from pathlib import Path
from typing import Union
import cv2
import dlib
from gwpycore.core.gw_exceptions import GWValueError


def crop_to_face(image_file: Union[Path, str], new_image_file: Union[Path, str], shoulder_factor=1.5):
    image_file = str(image_file)
    new_image_file = str(new_image_file)
    image = cv2.imread(image_file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    detector = dlib.get_frontal_face_detector()
    faces = detector(gray)

    if len(faces) <= 0:
        raise GWValueError(f'No face was detected within {image_file}')

    # Get the coordinates of the (first) face
    x, y, w, h = faces[0]

    # Crop the image to just the head and shoulders
    crop_x = x + w
    crop_y = y + h * shoulder_factor
    cropped_image = image[y:crop_y, x:crop_x]

    cv2.imwrite(new_image_file, cropped_image)




