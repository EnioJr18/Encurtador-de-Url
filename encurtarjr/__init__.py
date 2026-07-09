from flask import Flask

from config import get_config
from encurtarjr.extensions import bcrypt, db, login_manager, migrate
from encurtarjr.models import User
from encurtarjr.routes.auth_routes import auth_bp
from encurtarjr.routes.main_routes import main_bp
from encurtarjr.routes.url_routes import url_bp


def create_app(config_object=None):
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config.from_object(config_object or get_config())

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(url_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
