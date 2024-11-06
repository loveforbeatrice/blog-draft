
import os

class Config:
    # SQLite database URI for local development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking to save resources
    SECRET_KEY = os.urandom(24)  # Randomly generated secret key for session security
