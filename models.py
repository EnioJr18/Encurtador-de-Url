from flask_sqlalchemy import SQLAlchemy # type: ignore


db = SQLAlchemy()

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(100), unique=True, nullable=False)
    click_count = db.Column(db.Integer, default=0)
    acesso_data = db.Column(db.DateTime)
