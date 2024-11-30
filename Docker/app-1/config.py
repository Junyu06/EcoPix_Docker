import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    SESSION_TYPE = 'filesystem'