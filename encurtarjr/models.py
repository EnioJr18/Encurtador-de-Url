from flask_login import UserMixin

from encurtarjr.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    urls = db.relationship("URL", backref="user", lazy=True)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(100), unique=True, nullable=False)
    click_count = db.Column(db.Integer, default=0)
    acesso_data = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
