from flask import Flask, session
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from webapp.cache import cache
from webapp.db import db
from webapp.marketplace.models import Category, Product, ShoppingCart
from webapp.marketplace.views import blueprint as marketplace_blueprint
from webapp.marketplace.forms import SearchForm
from webapp.user.models import User
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

    @app.context_processor
    def utility_processor():
        form_search = SearchForm()
        form_search.search_input.data = ''

        if current_user.is_authenticated:
            products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
            unique_products_in_cart = len(products_in_cart)
            if products_in_cart:
                products_in_cart = {product.products.id: product.quantity for product in products_in_cart}
        else:
            unique_products_in_cart = session.get('unique_products_in_cart', None)
            products_in_cart = session.get('shopping_cart', None)
            if products_in_cart:
                products_in_cart = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}

        @cache.cached(timeout=18000, key_prefix='dropdown_categories')
        def dropdown_categories():
            categories = Category.query.filter(Category.parent_id.is_(None)).all()
            result = [sub_categories for category in categories for sub_categories in category.drilldown_tree()]
            return result

        return dict(dropdown_categories=dropdown_categories,
                    search_form=form_search,
                    products_in_cart=products_in_cart,
                    number_products_in_cart=unique_products_in_cart)

    return app
