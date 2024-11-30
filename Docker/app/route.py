# route.py
from flask import Blueprint, request, jsonify, make_response
import os

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

# Dynamically set USER_DB using environment variables
USERNAME = os.getenv("USERNAME", "default_user")  # Default to 'default_user' if not provided
UPASSWORD = os.getenv("UPASSWORD", "default_password")  # Default to 'default_password' if not provided

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
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie("auth_token", f"{username}_auth_cookie", httponly=True)
        return response, 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@routes.route('/protected', methods=['GET'])
def protected():
    # Check the cookie
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        return jsonify({"message": "Unauthorized"}), 401

    # Validate token (you might want a more secure validation method)
    username = auth_token.split("_auth_cookie")[0]
    if username in USER_DB:
        return jsonify({"message": f"Hello, {username}"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401
