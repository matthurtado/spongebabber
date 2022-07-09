import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ON_HEROKU = os.environ.get('ON_HEROKU')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if(ON_HEROKU):
        # Have to do this because Heroku is a dumb piece of shit
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USERNAME = os.environ.get('USERNAME')