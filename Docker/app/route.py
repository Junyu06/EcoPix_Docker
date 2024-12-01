# route.py
from flask import Blueprint, request, jsonify, make_response, session, send_from_directory
from flask_session import Session
from app.indexer import PhotoIndexer
from app.photolist import get_photo_list
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
        return get_photo_list()
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
