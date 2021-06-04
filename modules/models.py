from . import db


class GalleryModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickled_gallery = db.Column(db.PickleType, nullable=False)
