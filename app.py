import os
from flask import Flask # type: ignore
from models import db
from controllers import main

app = Flask(__name__)


uri = os.environ.get('DATABASE_URL', 'sqlite:///urls.db')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)