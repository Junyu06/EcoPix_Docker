from flask import Flask
from flask_session import Session
from app.route import routes  # Import the Blueprint
from app.db import db
from flask_sqlalchemy import SQLAlchemy
import os
import secrets

app = Flask(__name__)

#config flask-session
app.config['SESSION_TYPE'] = 'filesystem' #store session data in a filesystem
app.config['SECRET_KEY'] = secrets.token_hex(16) 
database_uri = os.getenv('DATABASE_URI', 'sqlite:///default.db')  # Fallback to SQLite if not set
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)
db.init_app(app)

#@app.before_first_request
def create_tables():
    """Create tables if they do not exist."""
    with app.app_context():
        db.create_all()

# Register the Blueprint
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15381)
