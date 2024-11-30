from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy object
db = SQLAlchemy()

# Define the Photo model
class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(1024), unique=True, nullable=False)
    thumbnail_path = db.Column(db.String(1024))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    gps_latitude = db.Column(db.Float)
    gps_longitude = db.Column(db.Float)
    camera_model = db.Column(db.String(255))
    focal_length = db.Column(db.Float)
    lens_model = db.Column(db.String(255))

    def __repr__(self):
        return f'<Photo {self.filename}>'
