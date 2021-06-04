import requests
from PIL import Image, ImageFilter, ImageEnhance
from zipfile import ZipFile
from random import randint
import io
import base64
import pickle
from flask import session
from .models import GalleryModel
from . import db


class Gallery:
    """
    A class to represent a gallery with images.

    ...

    Attributes
    ----------
    _pictures : list
        list of images

    Methods
    -------
    get_picture_objects(self):
        Returns picture objects.
    -------
    save_gallery(self):
        Returns zip file converted to io.BytesIO object.
    -------
    add_picture(self):
        Appends picture to gallery.
    -------
    delete_picture(self):
        Deletes picture from gallery.

    """

    def __init__(self, pictures=[]):
        self._pictures = pictures

    def get_picture_objects(self):
        return self._pictures

    def save_gallery(self):
        zip_file_bytes_io = io.BytesIO()
        with ZipFile(zip_file_bytes_io, 'w') as zip_file:
            for i, picture_object in enumerate(self.get_picture_objects(), 1):
                name = 'picture' + str(i)
                file_object = io.BytesIO()
                picture = picture_object.get_picture()
                picture.save(file_object, "PNG")
                picture.close()
                zip_file.writestr(
                    name + ".png", file_object.getvalue())
        zip_file_bytes_io.seek(0)
        return zip_file_bytes_io

    def add_picture(self, picture):
        self._pictures.append(picture)

    def delete_picture(self, index):
        del self._pictures[index]
        for new_index, picture in enumerate(self._pictures, 1):
            picture.set_id(new_index)


class PictureObject:
    """
    A class to represent a Picture object.

    ...

    Attributes
    ----------
    _id : int
        Id of Picture object
    ----------
    _picture : PIL object
        Image that Picture Object contains

    Methods
    -------
    get_picture_url(self, search):
        Helper function, returns url to UnsplashSource API.
    -------
    get_picture(self):
        Returns image that Picture Object contains.
    -------
    get_bytes_picture(self):
        Returns image that Picture Object contains as io.BytesIO() object that <img src=""> container can display.
    -------
    delete_picture(self):
        Deletes picture from gallery.
    -------
    change_blur(self, intensity=2):
        Applies blur to image.
    -------
    change_brightness(self, factor=1.5):
        changes brightness of image.
    -------
    transpose(self):
        Transposes image (left to right).

    """

    urls = {
        'getPicture': 'https://source.unsplash.com/1600x900/',
        'getPictureSquare': 'https://source.unsplash.com/900x900/',
    }

    def __init__(self, id, search):
        self._id = id
        url = self.get_picture_url(search)
        self._picture = Image.open(requests.get(url, stream=True).raw)

    def get_picture_url(self, search):
        if randint(0, 4) == 4:
            return self.urls['getPictureSquare'] + '?' + ','.join(search.split()) + f'&sig={self._id}'
        else:
            return self.urls['getPicture'] + '?' + ','.join(search.split()) + f'&sig={self._id}'

    def get_picture(self):
        return self._picture

    def get_bytes_picture(self):
        buffered = io.BytesIO()
        self._picture.save(buffered, format="PNG")
        picture_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f'data:image/png;base64,{picture_str}'

    def get_id(self):
        return self._id

    def set_id(self, new_id):
        self._id = new_id

    def change_blur(self, intensity=2):
        self._picture = self.get_picture().filter(
            ImageFilter.GaussianBlur(intensity))

    def change_brightness(self, factor=1.5):
        enhancer = ImageEnhance.Brightness(self._picture)
        self._picture = enhancer.enhance(factor)

    def transpose(self):
        self._picture = self.get_picture().transpose(Image.FLIP_LEFT_RIGHT)


class FileTransfer:
    """
    A class that helps website get gallery from database between different routes.

    ...
    Methods
    -------
    make_gallery_model_object(gallery):
        Makes gallery object and returns its database id.
    -------
    unpickle_gallery():
        Returns unpickled gallery.

    """

    def make_gallery_model_object(gallery):
        handle = io.BytesIO()
        pickle.dump(gallery, handle)
        new_gallery = GalleryModel(pickled_gallery=handle)
        db.session.add(new_gallery)
        db.session.commit()
        return new_gallery.id

    def unpickle_gallery():
        id = session['gallery_id']
        pickled = GalleryModel.query.get_or_404(id)
        handle = pickled.pickled_gallery
        handle.seek(0)
        return pickle.load(handle)
