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
    gps_latitude = db.Column(db.Float, nullable=True)  # GPS latitude metadata
    gps_longitude = db.Column(db.Float, nullable=True)  # GPS longitude metadata
    camera_model = db.Column(db.String(255))  # Camera model metadata
    focal_length = db.Column(db.Float)  # Focal length metadata
    lens_model = db.Column(db.String(255))  # Lens model metadata

    # Relationship to the Album model
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    album = db.relationship('Album', backref='photos', lazy=True)

    gps_cluster_id = db.Column(db.Integer, db.ForeignKey('gps_clusters.id'), nullable=True)
    
    def __repr__(self):
        return f'<Photo {self.filename}>'

class GPSCluster(db.Model):
    __tablename__ = 'gps_clusters'

    id = db.Column(db.Integer, primary_key=True)
    cluster_latitude = db.Column(db.Float, nullable=False)
    cluster_longitude = db.Column(db.Float, nullable=False)
    photo_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<GPSCluster ({self.cluster_latitude}, {self.cluster_longitude})>'
