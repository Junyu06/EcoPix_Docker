from flask import jsonfify, request, currrent_app
from sqlalchemy import desc, func
from app.db import Photo

def get_photo_list():
    #logic for the /photo.list route
    #returns a list of photos with optional oredering
    try:
        order = request.args.get('order','new-two-old').lower() # default to 'new-to-old'
        query = Photo.query 
        if order == 'new-to-old':
            query = query.order_by(desc(Photo.creation_date))
        elif order == 'old-to-new':
            query = query.order_by(Photo.creation_date)
        elif order == 'a-z':
            query = query.order_by(Photo.filename)
        elif order == 'z-a':
            query = query.order_by(desc(Photo.filename))
        elif order == 'random':
            query = query.order_by(func.random())

        photos = query.all()
        photo_list = [
            {
                "id": photo.id,
                "filename": photo.filename,
                "thumbnail_path": photo.thumbnail_path,
                "creation_date": photo.creation_date.isoformate() if photo.creation_date else None,
                "gps_latitude": photo.gps_latitude,
                "gps_longitude": photo.gps_longitude,
                "camera_model": photo.camera_model, 
            }
            for photo in photos
        ]

        return jsonfify(photo_list),200
    except Exception as e:
        currrent_app.logger.error(f"Error in /photo/list: {str(e)}")
        return jsonfify({"message":"An error occurred while fetching the photo list.", "error":str(e)}),500