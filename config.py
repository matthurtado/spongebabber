import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class EnvVariableNotSet(Exception):
    pass


class _Config:
    def __init__(self):
        self.ON_HEROKU = os.getenv("ON_HEROKU")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
        self.USERNAME = os.getenv("USERNAME")
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
        self.IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")
        self.FLASK_ENV = os.getenv("FLASK_ENV")

        self._check_env_vars()
        self._modify_envs()

    def _modify_envs(self):
        self._dumb_heroku()
        self._track_sqlalchemy_modifications()

    def _track_sqlalchemy_modifications(self, track_them=False):
        self.SQLALCHEMY_TRACK_MODIFICATIONS = track_them

    # Fixing Heroku's environment variables
    def _dumb_heroku(self):
        if(self.ON_HEROKU == "True"):
            self.SQLALCHEMY_DATABASE_URI = self.SQLALCHEMY_DATABASE_URI.replace("://", "ql://", 1)
        else:
            self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    def _check_env_vars(self):
        for v in dir(self):
            if getattr(self, v) is None and not v.startswith("__"):
                print("ENV VARIABLES LOAD: FAIL")
                raise EnvVariableNotSet(f"{v} NOT SET!")
        print("ENV VARIABLES LOAD: SUCCESS")


env = _Config()
