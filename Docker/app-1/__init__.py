from flask import Flask
from app.db import init_db
from app.indexer import init_indexer
import secrets
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object("app.config.Config")
    
    # Set secret key for session management
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
    
    # Configure session
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 hour session lifetime
    )
    from flask import jsonify

def create_app():
    app = Flask(__name__)
    
    # ... other configurations ...

    @app.errorhandler(Exception)
    def handle_error(error):
        """Global error handler to ensure JSON responses"""
        response = {
            'error': str(error),
            'message': 'An unexpected error occurred'
        }
        return jsonify(response), 500

    # ... rest of your app setup ...
    
    # Initialize the database
    init_db(app)
    
    # Initialize the photo indexer
    init_indexer(app)
    
    # Register routes blueprint
    from app.route import bp
    app.register_blueprint(bp)

    return app