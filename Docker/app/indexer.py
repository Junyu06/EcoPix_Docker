import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from app.db import db, Photo
import logging
from flask import current_app

class PhotoIndexer:
    #define the config
    def __init__(self, photo_dir="/Photos", thumbnail_dir="/Photos/thumbnail"):
        self.photos_dir = photo_dir
        self.thumbnail_dir=thumbnail_dir
        self.supported_formats={'.jpg','.jpeg','.png','.gif'}

    #create thumbnail direcotry if it doesn't exist
    def setup_direcotries(self):
        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)

    #convert image date time
    def get_image_datetime(self, image_path):
        try:
            exif_dict = piexif.load(image_path)
            if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            logging.warning(f"Could not read EXIF date for {image_path}: {str(e)}")
        
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(image_path))

    def get_exif(self, image_path):
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        return {
            TAGS.get(tag, tag): value
            for tag, value in exif_data.items()
        }
    
    #convert gps info
    def get_decimal_from_dms(self, dms, ref):
        degrees = dms[0]
        minutes = dms[1]
        seconds = dms[2]
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal

    def get_gps_data(self, exif_data):
        if 'GPSInfo' not in exif_data:
            return None
        gps_info = exif_data['GPSInfo']
        gps_data = {}
        for key in gps_info.keys():
            name = GPSTAGS.get(key, key)
            gps_data[name] = gps_info[key]

        # Extract latitude and longitude
        if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
            lat = self.get_decimal_from_dms(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef'])
            lon = self.get_decimal_from_dms(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
            return {"latitude": lat, "longitude": lon}
        return None

    def get_camera_details(self, exif_data):
    #"""Extract camera-related details from EXIF data."""
        if not exif_data:
            return None

        camera_details = {}

        # Camera model
        if "Model" in exif_data:
            camera_details["camera_model"] = exif_data["Model"]

        # Focal length
        if "FocalLength" in exif_data:
            focal_length = exif_data["FocalLength"]
            if isinstance(focal_length, tuple):
                # Convert fractional focal length to float
                camera_details["focal_length"] = focal_length[0] / focal_length[1]
            else:
                camera_details["focal_length"] = focal_length

        # Lens information (if available)
        if "LensModel" in exif_data:
            camera_details["lens_model"] = exif_data["LensModel"]

        return camera_details
    
    #generate thunbnail
    def generate_thumbnail(self, image_path):
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
    
    #index photos
    def index_photos(self):
        """Index all photos in the photos directory"""
        self.setup_direcotries()  # Fix typo in method name
        
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
                    
                    try:
                        # Generate thumbnail
                        thumbnail_path = self.generate_thumbnail(full_path)
                        if not thumbnail_path:
                            continue
                        
                        # Get EXIF data
                        exif_data = self.get_exif(full_path)
                        
                        # Get creation time
                        creation_time = self.get_image_datetime(full_path)
                        
                        # Get GPS data
                        gps_data = self.get_gps_data(exif_data)
                        lat = gps_data.get("latitude") if gps_data else None
                        lon = gps_data.get("longitude") if gps_data else None
                        
                        # Get camera details
                        camera_details = self.get_camera_details(exif_data)
                        camera_model = camera_details.get("camera_model") if camera_details else None
                        focal_length = camera_details.get("focal_length") if camera_details else None
                        lens_model = camera_details.get("lens_model") if camera_details else None
                        
                        # Create new photo record
                        new_photo = Photo(
                            filename=filename,
                            filepath=full_path,
                            thumbnail_path=thumbnail_path,
                            creation_date=creation_time,
                            gps_latitude=lat,
                            gps_longitude=lon,
                            camera_model=camera_model,
                            focal_length=focal_length,
                            lens_model=lens_model
                        )
                        
                        db.session.add(new_photo)
                    
                    except Exception as e:
                        logging.error(f"Error indexing photo {full_path}: {str(e)}")
            
            # Commit after processing each directory to avoid large transactions
            db.session.commit()

    
    #Initialize the indexer with the Flask app context
    @staticmethod
    def init_indexer():
        with current_app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Create and run indexer
            indexer = PhotoIndexer()
            indexer.index_photos()