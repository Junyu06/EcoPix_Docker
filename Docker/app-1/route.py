from flask import Blueprint, request, jsonify, session, current_app
import os
from functools import wraps
import secrets

# Create a Blueprint for our routes
bp = Blueprint('routes', __name__)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/api/login', methods=['POST'])
def login():
    """Handle user login and set session cookie"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Get credentials from environment variables
    correct_username = os.getenv('USERNAME')
    correct_password = os.getenv('UPASSWORD')
    
    # Check credentials
    if data['username'] == correct_username and data['password'] == correct_password:
        # Generate session token
        session['user_id'] = secrets.token_hex(16)
        session['username'] = data['username']
        
        return jsonify({
            'message': 'Login successful',
            'user_id': session['user_id']
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Clear session cookie"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@bp.route('/api/check-auth', methods=['GET'])
@login_required
def check_auth():
    """Check if user is authenticated"""
    return jsonify({
        'authenticated': True,
        'username': session.get('username')
    })