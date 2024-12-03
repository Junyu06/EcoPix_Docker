from flask import request, current_app, jsonify, session
from sqlalchemy import desc, func
from app.db import Photo, Album
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.db import db, Album, Photo

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
                "filepath": photo.filepath,
                "folderpath": photo.folder_path,
                "thumbnail_url": f"/pic/thumbnail/{photo.thumbnail_path.split('/')[-1]}" if photo.thumbnail_path else None,  # Hosted URL
                "photo_url": f"/pic/photos/{photo.filepath.replace('/Photos/', '')}" if photo.filepath else None,  # Hosted URL
                "creation_date": photo.creation_date.isoformat() if photo.creation_date else None,
                "gps_latitude": photo.gps_latitude,
                "gps_longitude": photo.gps_longitude,
                "camera_model": photo.camera_model,
                "focal_length": photo.focal_length,
                "lens_model": photo.lens_model,
                "album": {
                    "id": photo.album.id,
                    "name": photo.album.name,
                    "creation_date": photo.album.creation_date.isoformat()
                } if photo.album else None,
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

def get_album_photo_list():
    try:
        # Query parameters
        order = request.args.get('order', 'new-to-old').lower()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        album_id = request.args.get('album_id')

        if not album_id:
            return jsonify({"message": "album_id is required"}), 400

        # Base query
        query = Photo.query.filter(Photo.album_id == album_id)

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
                "filepath": photo.filepath,
                "folderpath": photo.folder_path,
                "thumbnail_url": f"/pic/thumbnail/{photo.thumbnail_path.split('/')[-1]}" if photo.thumbnail_path else None,  # Hosted URL
                "photo_url": f"/pic/photos/{photo.filepath.replace('/Photos/', '')}" if photo.filepath else None,  # Hosted URL
                "creation_date": photo.creation_date.isoformat() if photo.creation_date else None,
                "gps_latitude": photo.gps_latitude,
                "gps_longitude": photo.gps_longitude,
                "camera_model": photo.camera_model,
                "focal_length": photo.focal_length,
                "lens_model": photo.lens_model,
                "album": {
                    "id": photo.album.id,
                    "name": photo.album.name,  # Correctly access the `name` attribute
                    "creation_date": photo.album.creation_date.isoformat()
                } if photo.album else None,
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

def get_album_action():
    try:
        # Query parameters
        album_action = request.args.get('action')
        album_id = request.args.get('album_id', type=int)
        album_name = request.args.get('album_name')

        # Ensure album_action is provided
        if not album_action:
            return jsonify({"message": "album_action is required"}), 400

        # Handle 'add' action
        if album_action.lower() == 'add':
            if not album_name:
                return jsonify({"message": "album_name is required for 'add' action"}), 400
            
            # Check if an album with the same name already exists
            existing_album = Album.query.filter_by(name=album_name).first()
            if existing_album:
                return jsonify({"message": f"Album with name '{album_name}' already exists"}), 400
            
            # Create and add a new album
            new_album = Album(name=album_name)
            db.session.add(new_album)
            db.session.commit()
            return jsonify({"message": f"Album '{album_name}' added successfully", "album_id": new_album.id}), 200

        # Handle 'delete' action
        elif album_action.lower() == 'delete':
            if not album_id:
                return jsonify({"message": "album_id is required for 'delete' action"}), 400
            
            # Find the album by ID
            album = Album.query.get(album_id)
            if not album:
                return jsonify({"message": f"Album with ID '{album_id}' not found"}), 404

            # Delete the album
            db.session.delete(album)
            db.session.commit()
            return jsonify({"message": f"Album with ID '{album_id}' deleted successfully"}), 200

        # Invalid action
        else:
            return jsonify({"message": "Invalid album_action. Use 'add' or 'delete'"}), 400

    except Exception as e:
        current_app.logger.error(f"Error in /album/action: {str(e)}")
        return jsonify({"message": "An error occurred while performing the album action.", "error": str(e)}), 500

def add_delete_from_album():
    try:
        # Query parameters from the request
        album_id = request.args.get('album_id', type=int)
        photo_id = request.args.get('photo_id', type=int)

        # Validate inputs
        if not album_id or not photo_id:
            return jsonify({"message": "Both album_id and photo_id are required"}), 400

        # Find the album
        album = Album.query.get(album_id)
        if not album:
            return jsonify({"message": f"Album with id {album_id} not found"}), 404

        # Find the photo
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"message": f"Photo with id {photo_id} not found"}), 404

        # Check if the photo is already in the album
        if photo in album.photos:
            # Remove the photo from the album
            photo.album_id = None
            db.session.commit()
            return jsonify({"message": f"Photo {photo_id} removed from album {album_id}"}), 200
        else:
            # Add the photo to the album
            photo.album_id = album_id
            db.session.commit()
            return jsonify({"message": f"Photo {photo_id} added to album {album_id}"}), 200

    except Exception as e:
        current_app.logger.error(f"Error in /album/photo/action: {str(e)}")
        return jsonify({"message": "An error occurred while performing the album photo action.", "error": str(e)}), 500