from flask import session
from flask_login import current_user

from webapp import cache
from webapp.marketplace.models import Product, ShoppingCart


@cache.memoize(timeout=600)
def search_products_by_text(search_text):
    products_query = Product.query.filter(Product.name.ilike(f'%{search_text}%')).all()
    return products_query


def get_product_by_id(product_id):
    product_query = Product.query.filter(Product.id == product_id).first()
    return product_query


def get_products_in_cart():
    if current_user.is_authenticated:
        products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
        if products_in_cart:
            products_in_cart = {product.product_info.id: product.quantity for product in products_in_cart}
        else:
            products_in_cart = None
    else:
        products_in_cart = session.get('shopping_cart', None)
        if products_in_cart:
            products_in_cart = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}

    return products_in_cart


def get_unique_products_in_cart():
    if current_user.is_authenticated:
        unique_products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).count()
    else:
        unique_products_in_cart = session.get('unique_products_in_cart', None)
    return unique_products_in_cart
