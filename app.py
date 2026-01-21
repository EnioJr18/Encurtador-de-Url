import os
from flask import Flask # type: ignore
from models import db
from controllers import main

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_senha_muito_dificil_e_secreta')


uri = os.getenv('DATABASE_URL', 'sqlite:///urls.db')


if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(main)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)