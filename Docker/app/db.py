from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False, unique=True)  # Index for quick lookups
    thumbnail_path = db.Column(db.String(512))
    creation_date = db.Column(db.DateTime, nullable=False, index=True)  # Index for time-based queries
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # GPS coordinates
    gps_latitude = db.Column(db.Float)
    gps_longitude = db.Column(db.Float)
    
    # Create indexes for better query performance
    __table_args__ = (
        db.Index('idx_filepath', 'filepath'),
        db.Index('idx_creation_date', 'creation_date'),
        db.Index('idx_gps', 'gps_latitude', 'gps_longitude')
    )

def init_db(app):
    db.init_app(app)