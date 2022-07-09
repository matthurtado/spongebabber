from ipaddress import ip_address
from app import db, serializer

class LogRequest(db.Model, serializer.Serializer):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(1024))
    text_x_pos = db.Column(db.Integer)
    text_y_pos = db.Column(db.String(64))
    target_width_ratio = db.Column(db.Float)
    sponge_the_text = db.Column(db.Boolean)
    ip_address=db.Column(db.String(128))
    timestamp=db.Column(db.DateTime)