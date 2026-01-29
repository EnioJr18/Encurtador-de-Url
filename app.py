import os
from flask import Flask # type: ignore
from models import db, User, URL # Importando as classes do banco
from controllers import main
from flask_login import LoginManager # type: ignore
from flask_bcrypt import Bcrypt # type: ignore

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_senha_muito_dificil_e_secreta')

# --- INICIALIZAÇÃO DAS EXTENSÕES ---

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = 'main.login' 

login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- FIM DAS EXTENSÕES ---

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