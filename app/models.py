from email.policy import default
from ipaddress import ip_address
from app import db, serializer


class LogRequest(db.Model, serializer.Serializer):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024))
    text_x_pos = db.Column(db.Integer)
    text_y_pos = db.Column(db.String(64))
    target_width_ratio = db.Column(db.Float)
    sponge_the_text = db.Column(db.Boolean)
    ip_address=db.Column(db.String(128))
    imgur_link=db.Column(db.String(1024))
    timestamp=db.Column(db.DateTime)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, serializer.Serializer):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime)
    requests_per_day = db.Column(db.Integer, default = 50)
    upload_to_imgur = db.Column(db.Boolean, default = False)
