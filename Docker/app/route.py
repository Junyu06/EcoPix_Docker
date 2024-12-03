# route.py
from flask import Blueprint, request, jsonify, make_response, session, send_from_directory
from flask_session import Session
from app.indexer import PhotoIndexer
from app.photolist import get_photo_list, get_album_photo_list, get_album_action
from sqlalchemy import desc, func
from app.db import db, Album, Photo
import os

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# Dynamically set USER_DB using environment variables
USERNAME = os.getenv("USERNAME", "default_user")  # Default to 'default_user' if not provided
UPASSWORD = os.getenv("UPASSWORD", "default_password")  # Default to 'default_password' if not provided

THUMBNAIL_DIR = "/Photos/thumbnail"  # Adjust this to the actual path
PHOTO_DIR = "/Photos"  # Adjust this to the actual path

USER_DB = {
    USERNAME: UPASSWORD
}

@routes.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate credentials
    if username in USER_DB and USER_DB[username] == password:
        # Generate response with cookie
        # response = make_response(jsonify({"message": "Login successful"}))
        # response.set_cookie("auth_token", f"{username}_auth_cookie", httponly=True)
        # return response, 200
        session['username'] = username
        return jsonify({"message": "Login sucessful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@routes.route('/protected', methods=['GET'])
def protected():
    # Check if the user is logged in by verifying the session
    if 'username' in session:
        username = session['username']  # Retrieve the username from the session
        return jsonify({"message": f"Hello, {username}"}), 200
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401

@routes.route('/photo/index', methods=['GET'])
def index():
    """
    Route to start indexing the photo library.
    Only accessible to logged-in users with a valid session.
    """
    # Verify the user session
    if 'username' in session:
        try:
            # Start the photo indexing process
            PhotoIndexer.init_indexer()  # Triggers indexing manually
            return jsonify({"message": "Indexing started successfully."}), 200
        except Exception as e:
            # Log and return error details
            current_app.logger.error(f"Error during indexing: {str(e)}")
            return jsonify({"message": "Indexing failed", "error": str(e)}), 500
    else:
        return jsonify({"message": "Unauthorized access."}), 401
    
@routes.route('/photo/list', methods=['GET'])
def photo_list():
    if 'username' in session:
        stuff = get_photo_list()
        print(stuff)
        return stuff
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401

#dont forget to chagne get list to the actual website
@routes.route('/pic/thumbnail/<path:filename>', methods=['GET'])
def serve_thumbnail(filename):
    """
    Serve a thumbnail image from the thumbnail directory.
    """
    if 'username' in session:
        try:
            return send_from_directory(THUMBNAIL_DIR, filename, as_attachment=False)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401
    


@routes.route('/pic/photos/<path:filename>', methods=['GET'])
def serve_photo(filename):
    """
    Serve an actual photo from the photo directory.
    """
    if 'username' in session:
        try:
            return send_from_directory(PHOTO_DIR, filename, as_attachment=False)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401
    
@routes.route('/folders', methods=['GET'])
def list_subfolders():
    base_path = request.args.get('path', '/Photos')  # Default to root directory
    if 'username' in session:
        try:
            subfolders = [
                {"name": name, "path": os.path.join(base_path, name)}
                for name in os.listdir(base_path)
                if os.path.isdir(os.path.join(base_path, name))
            ]
            return jsonify({"path": base_path, "subfolders": subfolders}), 200
        except Exception as e:
            logging.error(f"Error listing subfolders in {base_path}: {str(e)}")
            return jsonify({"error": "Unable to fetch subfolders", "message": str(e)}), 500
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401

    

@routes.route('/folders/photos', methods=['GET'])
def list_photos_in_folder():
    folder_path = request.args.get('path', '/Photos')  # Default to root directory
    if 'username' in session:
        try:
            photos = Photo.query.filter(Photo.folder_path == folder_path).all()
            photo_list = [
                {
                    "id": photo.id,
                    "filename": photo.filename,
                    "thumbnail_url": f"/pic/thumbnail/{photo.thumbnail_path.split('/')[-1]}",
                    "photo_url": f"/pic/photos/{photo.filepath.replace('/Photos/', '')}",
                    "creation_date": photo.creation_date.isoformat() if photo.creation_date else None,
                    "camera_model": photo.camera_model,
                    "focal_length": photo.focal_length,
                    "lens_model": photo.lens_model
                }
                for photo in photos
            ]
            return jsonify({"path": folder_path, "photos": photo_list}), 200
        except Exception as e:
            logging.error(f"Error listing photos in folder {folder_path}: {str(e)}")
            return jsonify({"error": "Unable to fetch photos", "message": str(e)}), 500
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401

    

@routes.route('/albums', methods=['GET'])
def list_albums():
    if 'username' in session:
        albums = Album.query.all()
        return jsonify([
            {
                "id": album.id,
                "name": album.name,
                "description": album.description,
                "creation_date": album.creation_date.isoformat(),
                "photo_count": len(album.photos)  # Count photos in the album
            }
            for album in albums
        ])
    else:
        #print("The session id is")
        return jsonify({"message": "Unauthorized"}), 401
    

@routes.route('/album/photos', methods=['GET'])
def list_photos_in_album():
    if 'username' in session:
        stuff = get_album_photo_list()
        print(stuff)
        return stuff
    else:
        return jsonify({"message": "Unauthorized"}), 401

@routes.route('/album/action', methods=['GET'])
def action_in_album():
    if 'username' in session:
        stuff = get_album_action()
        print(stuff)
        return stuff
    else:
        return jsonify({"message": "Unauthorized"}), 401
