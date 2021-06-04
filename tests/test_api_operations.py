from zipfile import ZipFile
from copy import copy
import PIL
import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
from modules.api_operations import PictureObject, Gallery


def test_picture():
    image = PictureObject(1, 'mountain')
    assert image.get_id() == 1
    assert image.get_picture() is not None
    assert isinstance(image.get_bytes_picture(), str) is True


def test_picture_size(monkeypatch):
    def return_four(*args):
        return 4
    monkeypatch.setattr('modules.api_operations.randint', return_four)

    image = PictureObject(5, 'mountain')
    assert image.get_id() == 5
    assert image.get_picture() is not None
    width, height = image.get_picture().size
    assert width == 900
    assert height == 900

    for i in range(4):
        def return_number(*args):
            return i
        monkeypatch.setattr('modules.api_operations.randint', return_number)

        image = PictureObject(i, 'tree')
        assert image.get_id() == i
        assert image.get_picture() is not None
        width, height = image.get_picture().size
        assert width == 1600
        assert height == 900



def test_picture_blur_brightness_transpose():
    image = PictureObject(1, 'mountain')
    image_copy = copy(image)
    image.change_blur(3)
    assert image != image_copy
    image_copy2 = copy(image)
    image.change_brightness(1.1)
    assert image != image_copy
    image_copy3 = copy(image)
    image.transpose()
    assert image != image_copy


def test_gallery():
    image1 = PictureObject(1, 'mountain')
    image2 = PictureObject(2, 'lake')
    image3 = PictureObject(3, 'water dog')
    gallery = Gallery([image1, image2])
    assert len(gallery.get_picture_objects()) == 2
    gallery.add_picture(image3)
    assert len(gallery.get_picture_objects()) == 3
    gallery.delete_picture(0)
    assert len(gallery.get_picture_objects()) == 2


def test_gallery_zip():
    image1 = PictureObject(1, 'mountain')
    image2 = PictureObject(2, 'lake')
    image3 = PictureObject(3, 'water dog')
    gallery = Gallery([image1, image2, image3])
    zipped_gallery = gallery.save_gallery()
    with ZipFile(zipped_gallery, 'w') as zip_file:
        assert zip_file.testzip() is None
