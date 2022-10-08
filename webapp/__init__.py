from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from webapp.cache import cache
from webapp.db import db
from webapp.user.models import User
from webapp.marketplace.models import Category
from webapp.marketplace.views import blueprint as marketplace_blueprint
from webapp.user.views import blueprint as user_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    cache.init_app(app)  # Подключение Кэша
    db.init_app(app)  # Инициализация БД
    migrate = Migrate(app, db)  # Для миграции-изменения структуры БД

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    app.register_blueprint(marketplace_blueprint)
    app.register_blueprint(user_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @cache.cached(timeout=18000, key_prefix='dropdown_categories')
    @app.context_processor
    def utility_processor():
        def dropdown_categories():
            categories = Category.query.filter(Category.parent_id.is_(None)).all()
            result = [sub_categories for category in categories for sub_categories in category.drilldown_tree()]
            return result

        return dict(dropdown_categories=dropdown_categories)

    return app
