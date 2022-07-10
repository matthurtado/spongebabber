from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
limiter = Limiter(app, key_func=get_remote_address)

from app import routes, models

if __name__ == '__main__':
    app.run(threaded=True, port=5000)