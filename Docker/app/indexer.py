import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from app.db import db, Photo
import logging

class PhotoIndexer:
    def __init__(self, photos_dir="/Photos", thumbnail_dir="/Photos/thumbnail"):
        self.photos_dir = photos_dir
        self.thumbnail_dir = thumbnail_dir
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif'}
        
    def setup_directories(self):
        """Create thumbnail directory if it doesn't exist"""
        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)

    def get_image_datetime(self, image_path):
        """Extract creation time from EXIF data or use file modification time"""
        try:
            exif_dict = piexif.load(image_path)
            if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            logging.warning(f"Could not read EXIF date for {image_path}: {str(e)}")
        
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(image_path))

    def get_gps_info(self, image_path):
        """Extract GPS coordinates from EXIF data"""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if not exif:
                    return None, None

                for tag_id in exif:
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag in exif[tag_id]:
                            sub_tag = GPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_tag] = exif[tag_id][gps_tag]

                        if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                            lat = self._convert_to_degrees(gps_data["GPSLatitude"])
                            lon = self._convert_to_degrees(gps_data["GPSLongitude"])
                            
                            if gps_data.get("GPSLatitudeRef", "N") == "S":
                                lat = -lat
                            if gps_data.get("GPSLongitudeRef", "E") == "W":
                                lon = -lon
                            
                            return lat, lon
        except Exception as e:
            logging.warning(f"Could not read GPS data for {image_path}: {str(e)}")
        
        return None, None

    def _convert_to_degrees(self, value):
        """Helper function to convert GPS coordinates to degrees"""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    def generate_thumbnail(self, image_path):
        """Generate thumbnail and return its path"""
        try:
            filename = os.path.basename(image_path)
            thumbnail_path = os.path.join(self.thumbnail_dir, f"thumb_{filename}")
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((300, 300))
                img.save(thumbnail_path, "JPEG")
            
            return thumbnail_path
        except Exception as e:
            logging.error(f"Failed to generate thumbnail for {image_path}: {str(e)}")
            return None

    def index_photos(self):
        """Index all photos in the photos directory"""
        self.setup_directories()
        
        for root, _, files in os.walk(self.photos_dir):
            # Skip thumbnail directory
            if root == self.thumbnail_dir:
                continue
                
            for filename in files:
                if os.path.splitext(filename)[1].lower() in self.supported_formats:
                    full_path = os.path.join(root, filename)
                    
                    # Check if photo is already indexed
                    existing_photo = Photo.query.filter_by(filepath=full_path).first()
                    if existing_photo:
                        continue
                    
                    # Generate thumbnail
                    thumbnail_path = self.generate_thumbnail(full_path)
                    if not thumbnail_path:
                        continue
                    
                    # Get image creation time and GPS coordinates
                    creation_time = self.get_image_datetime(full_path)
                    lat, lon = self.get_gps_info(full_path)
                    
                    # Create new photo record
                    new_photo = Photo(
                        filename=filename,
                        filepath=full_path,
                        thumbnail_path=thumbnail_path,
                        creation_date=creation_time,
                        gps_latitude=lat,
                        gps_longitude=lon
                    )
                    
                    db.session.add(new_photo)
                    
            # Commit after each directory to avoid large transactions
            db.session.commit()

def init_indexer(app):
    """Initialize the indexer with the Flask app context"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create and run indexer
        indexer = PhotoIndexer()
        indexer.index_photos()