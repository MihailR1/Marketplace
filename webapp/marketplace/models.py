from sqlalchemy.orm import relationship
from sqlalchemy_mptt.mixins import BaseNestedSets

from webapp.db import db
from webapp.user.models import User


class Category(db.Model, BaseNestedSets):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    category = relationship('Category', backref='products')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship('User', backref='products')
    name = db.Column(db.String(180), index=True, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    brand_name = db.Column(db.String(40))
    color = db.Column(db.String(20))
    gender = db.Column(db.String(7))
    size = db.Column(db.String(10))

    def __repr__(self):
        return f'<Product name {self.name}, id {self.id}, category {self.category}>'


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    product = relationship('Product', backref='photos')
    photos_path = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Photo {self.photos_path}, id {self.id}, product {self.product}>'


class User_favorite_product(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship('User', backref='User_favorite_products')
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    product = relationship('Product', backref='User_favorite_products')
    

    def __repr__(self):
        return f'<User_favorite_product {self.user_id}, {self.product_id}>'

