from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from webapp.model import db
from webapp.model import User
from webapp.user.views import blueprint as user_blueprint
from webapp.marketplace.views import blueprint as marketplace_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)  # Инициализация БД
    migrate = Migrate(app, db)  # Для миграции-изменения структуры БД

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    app.register_blueprint(user_blueprint)
    app.register_blueprint(marketplace_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app
