from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    '''Все данные о пользователе, которые будут храниться в БД.
    При регистрации обязательные поля - email и пароль'''

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True, nullable=False)
    phone_number = db.Column(db.String(12), index=True, unique=True, nullable=True)
    full_name = db.Column(db.String, nullable=True)
    shipping_adress = db.Column(db.String, nullable=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), index=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id}>'