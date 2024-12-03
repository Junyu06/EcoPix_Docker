from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy object
db = SQLAlchemy()

# Album model
class Album(db.Model):
    __tablename__ = 'album'  # Corrected to __tablename__
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)  # Album name must be unique
    description = db.Column(db.Text, nullable=True)  # Optional album description
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set to current time

    def __repr__(self):
        return f'<Album {self.name}>'

# Photo model
class Photo(db.Model):
    __tablename__ = 'photos'  # Corrected to __tablename__

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Photo file name
    filepath = db.Column(db.String(1024), unique=True, nullable=False)  # Full file path
    folder_path = db.Column(db.String(1024))  # Folder organization (optional)
    thumbnail_path = db.Column(db.String(1024))  # Path to the generated thumbnail
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set to current time
    gps_latitude = db.Column(db.Float)  # GPS latitude metadata
    gps_longitude = db.Column(db.Float)  # GPS longitude metadata
    camera_model = db.Column(db.String(255))  # Camera model metadata
    focal_length = db.Column(db.Float)  # Focal length metadata
    lens_model = db.Column(db.String(255))  # Lens model metadata

    # Relationship to the Album model
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    album = db.relationship('Album', backref='photos', lazy=True)

    def __repr__(self):
        return f'<Photo {self.filename}>'
