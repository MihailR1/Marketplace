from flask import session
from flask_login import current_user

from webapp.marketplace.models import Product, ShoppingCart
from webapp.services.service_send_sms import delete_symbols_from_phone_number
from webapp.user.models import User
from webapp import db


def search_products_by_text(search_text):
    products_query = Product.query.filter(Product.name.ilike(f'%{search_text}%')).all()
    return products_query


def get_product_by_id(product_id):
    product_query = Product.query.filter(Product.id == product_id).first()
    return product_query


def get_products_in_cart():
    if current_user.is_authenticated:
        products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                     ShoppingCart.is_shopping_cart_paid == False).all()
        if products_in_cart:
            products_in_cart = {product.product_info.id: product.quantity for product in products_in_cart}
        else:
            products_in_cart = None
    else:
        products_in_cart = session.get('shopping_cart', None)
        if products_in_cart:
            products_in_cart = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}

    return products_in_cart


def get_number_of_unique_products_in_cart():
    if current_user.is_authenticated:
        unique_products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                            ShoppingCart.is_shopping_cart_paid == False).count()
    else:
        unique_products_in_cart = len(session.get('shopping_cart', []))

    return unique_products_in_cart


def save_products_into_db_from_session_cart(user: User):
    products_in_cart = session.get('shopping_cart', None)

    if products_in_cart:
        products_in_session_cart = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}
        query_products = Product.query.filter(Product.id.in_(products_in_session_cart.keys())).all()
        user_products_in_cart = user.cart
        user_products_dict = {product.product_id: product.quantity for product in user_products_in_cart}

        for product in query_products:
            product_quantity_in_user_db = user_products_dict.get(product.id, 0)
            session_product_quantity = products_in_session_cart[product.id]
            total_quantity = product_quantity_in_user_db + session_product_quantity

            if product.id in user_products_dict.keys():
                for cart in user_products_in_cart:
                    if cart.product_id == product.id:
                        cart.quantity = total_quantity
                        break
            else:
                save_product_in_cart = ShoppingCart(user_id=user.id, product_id=product.id, quantity=total_quantity)
                db.session.add(save_product_in_cart)

        db.session.commit()


def save_unauthenticated_user_data_in_session(form):
    session['full_name'] = form.full_name.data
    session['shipping_adress'] = form.shipping_adress.data
    session['phone_number'] = delete_symbols_from_phone_number(form.phone_number.data)
    session['email'] = form.email.data
    session.modified = True
