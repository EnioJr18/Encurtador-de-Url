from flask import Flask  # type: ignore
from flask_bcrypt import Bcrypt  # type: ignore
from flask_login import LoginManager  # type: ignore

from config import get_config
from controllers import main
from models import User, db


app = Flask(__name__)
app.config.from_object(get_config())

# --- INICIALIZACAO DAS EXTENSOES ---

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "main.login"

login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- FIM DAS EXTENSOES ---

db.init_app(app)

app.register_blueprint(main)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
