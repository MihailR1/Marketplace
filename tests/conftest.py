import pytest

from webapp import create_app
from webapp.db import db
from webapp.user.models import User
from webapp.marketplace.models import Category, Product


# Инициализация flask приложения
@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# Для работы с моделями БД
@pytest.fixture(scope='function')
def client(app):
    yield app.test_client()
    app.test_client().get("/users/logout")


# В БД заранее занесен юзер
@pytest.fixture(scope='module')
def client_with_user(app):
    with app.test_client() as client_user:
        user = User(email='test@gmail.com')
        user.set_password('testing')
        db.session.add(user)
        db.session.commit()
        yield client_user


# Клиент с авторизованным юзером
@pytest.fixture(scope='function')
def client_with_loggined_user(app):
    with app.test_client() as client_with_user:
        auth_data = {'email': 'test@gmail.com', 'password': 'testing'}
        client_with_user.post('/users/process-login', data=auth_data, follow_redirects=True)
        yield client_with_user


@pytest.fixture(scope='module')
def client_with_products(app):
    with app.app_context():
        category = Category(name='Одежда')
        db.session.add(category)
        db.session.commit()

        product1 = Product(category_id=category.id, user_id=1, name='Мужские ботинки', price='1990',
                           description='Просто мужжские ботинки', brand_name='Apple', color='черный', gender='М',
                           size='41', quantity=100)
        product2 = Product(category_id=category.id, user_id=1, name='Розовая женская куртка Armani', price='19990',
                           description='же', brand_name='Armani', color='розовый', gender='Ж', size='s', quantity=10)
        db.session.add(product1)
        db.session.add(product2)
        db.session.commit()
        yield app.test_client()
