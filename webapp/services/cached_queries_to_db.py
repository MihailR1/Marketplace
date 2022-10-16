from webapp import cache
from webapp.db import db
from webapp.marketplace.models import Category, Product, Photo, ShoppingCart


@cache.memoize(timeout=120)
def get_product_by_id(product_id):
    product_query = Product.query.filter(Product.id == product_id).first()
    return product_query


@cache.memoize(timeout=600)
def search_products_by_text(search_text):
    products_query = Product.query.filter(Product.name.ilike(f'%{search_text}%')).all()
    return products_query


@cache.memoize(timeout=5)
def number_of_unique_products_in_cart(current_user_id):
    number_of_products = ShoppingCart.query.filter(ShoppingCart.user_id == current_user_id).count()
    return number_of_products
