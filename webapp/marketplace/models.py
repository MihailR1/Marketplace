from datetime import datetime

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
    category = relationship('Category', backref='products', lazy='joined')
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship('User', backref='products')
    name = db.Column(db.String(180), index=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    brand_name = db.Column(db.String(40))
    color = db.Column(db.String(20))
    gender = db.Column(db.String(13))
    size = db.Column(db.String(15))
    quantity = db.Column(db.Integer, index=True, default=100)

    def __repr__(self):
        return f'<Product name {self.name}, id {self.id}, category {self.category}>'


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    product = relationship('Product', backref='photos')
    photos_path = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Photo {self.photos_path}, id {self.id}, product {self.product}>'


class UserFavoriteProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship('User', backref='user_favorite_products')
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    product = relationship('Product', backref='user_favorite_products')

    def __repr__(self):
        return f'<User_favorite_product {self.user_id}, {self.product_id}>'


class ShoppingOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_order_paid = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    user = relationship('User', backref='orders')
    order_number = db.Column(db.String(90))
    amount = db.Column(db.Integer)
    paid_datetime = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return f'<ShoppingOrder {self.id}, order id: {self.order_number}, user: {self.user_id}>'


class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id, ondelete='CASCADE'))
    order_id = db.Column(db.Integer, db.ForeignKey(ShoppingOrder.id, ondelete='CASCADE'))
    user = relationship('User', backref='cart')
    product_info = relationship('Product', backref='cart')
    order = relationship('ShoppingOrder', backref='cart')
    quantity = db.Column(db.Integer)
    is_shopping_cart_paid = db.Column(db.Boolean, default=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<ShoppingCart id {self.id}, user_id: {self.user_id}, products: {self.product_info}>'
