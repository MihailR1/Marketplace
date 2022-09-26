from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_mptt.mixins import BaseNestedSets

db = SQLAlchemy()


class User(db.Model, UserMixin):
    '''Все данные о пользователе, которые будут храниться в БД.
    При регистрации обязательные поля - email и пароль'''

    __tablename__ = 'all_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.String(12), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    shipping_adress = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), index=True)
    created_products = db.relationship("Product", lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id}>'


class Category(db.Model, BaseNestedSets):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    products = db.relationship("Product", backref='item', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.Column(db.String(50), db.ForeignKey('categories.name'))
    created_by = db.Column(db.Integer, db.ForeignKey('all_users.id'))
    name = db.Column(db.String(475), index=True, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    photos_path = db.Column(db.String, nullable=False)  # Путь до всех фото каталога
    description = db.Column(db.Text)
    brand_name = db.Column(db.String(40))
    color = db.Column(db.String(20))
    gender = db.Column(db.String(7))
    size = db.Column(db.String(10))

    def __repr__(self):
        return f'<Product name {self.name}, id {self.id}, category {self.category_id}>'
