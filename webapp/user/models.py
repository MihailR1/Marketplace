from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from webapp.db import db


class User(db.Model, UserMixin):
    '''Все данные о пользователе, которые будут храниться в БД.
    При регистрации обязательные поля - email и пароль'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.String(12), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    shipping_adress = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), index=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id}>'