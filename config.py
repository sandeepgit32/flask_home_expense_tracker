import os
from dotenv import load_dotenv
from datetime import timedelta
# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

load_dotenv('.env', verbose=True)


class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_PATH = 10 * 1024 * 1024  # restrict max upload image size to 10MB
    SQLALCHEMY_ECHO = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15) # Define the validity of a session for 15 minutes


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')