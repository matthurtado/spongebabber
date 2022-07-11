import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ON_HEROKU = os.environ.get('ON_HEROKU')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if(ON_HEROKU):
        # Have to do this because of Heroku incompatibility with Flask-SQLAlchemy
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USERNAME = os.environ.get('USERNAME')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID')
    IMGUR_CLIENT_SECRET = os.environ.get('IMGUR_CLIENT_SECRET')