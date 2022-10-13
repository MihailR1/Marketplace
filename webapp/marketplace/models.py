from sqlalchemy.orm import relationship
from sqlalchemy_mptt.mixins import BaseNestedSets

from webapp.db import db
from webapp.user.models import User


class Category(db.Model, BaseNestedSets):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = relationship('Category', backref='products')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship('User', backref='products')
    name = db.Column(db.String(75), index=True, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    photos_path = db.Column(db.String, nullable=False)  # Путь до всех фото каталога
    description = db.Column(db.Text)
    brand_name = db.Column(db.String(40))
    color = db.Column(db.String(20))
    gender = db.Column(db.String(7))
    size = db.Column(db.String(10))

    def __repr__(self):
        return f'<Product name {self.name}, id {self.id}, category {self.category}>'
