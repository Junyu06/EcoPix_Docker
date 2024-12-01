from flask import request, current_app, jsonify, session
from sqlalchemy import desc, func
from app.db import Photo

def get_photo_list():
    try:
        # Query parameters
        order = request.args.get('order', 'new-to-old').lower()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Base query
        query = Photo.query

        # Apply ordering
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

        # Apply pagination
        paginated_photos = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format response
        photo_list = [
            {
                "id": photo.id,
                "filename": photo.filename,
                "thumbnail_url": f"/pic/thumbnail/{photo.thumbnail_path.split('/')[-1]}",  # Hosted URL
                "photo_url": f"/pic/photos/{photo.filepath.split('/')[-1]}",  # Hosted URL
                "creation_date": photo.creation_date.isoformat() if photo.creation_date else None,
                "gps_latitude": photo.gps_latitude,
                "gps_longitude": photo.gps_longitude,
                "camera_model": photo.camera_model,
            }
            for photo in paginated_photos.items
        ]

        # Return JSON response
        return jsonify({
            "photos": photo_list,
            "total": paginated_photos.total,
            "page": paginated_photos.page,
            "pages": paginated_photos.pages,
            "per_page": paginated_photos.per_page,
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in /photo/list: {str(e)}")
        return jsonify({"message": "An error occurred while fetching the photo list.", "error": str(e)}), 500
