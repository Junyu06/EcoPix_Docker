from flask import Flask
from app.db import init_db
from app.indexer import init_indexer

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    
    # Initialize the database
    init_db(app)
    
    # Initialize the photo indexer
    init_indexer(app)

    @app.route("/")
    def home():
        return "Hello, EcoPix Docker!"

    return app