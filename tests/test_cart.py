import json

import pytest
from flask import session
from flask_login import current_user

from webapp import ShoppingCart


@pytest.fixture
def json_settings():
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    return headers


def test_unauth_user_add_product_with_quantity_1(client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': 1}
    with client_with_products:
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert session['shopping_cart'][str(product_settings['product_id'])] == 1
    assert response.json["is_available"] is True
    assert response.json["quantity"] == 100
    assert response.json["unique_products"] == 1


def test_unauth_user_add_product_with_quantity_5(client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': 5}
    with client_with_products:
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert session['shopping_cart'][str(product_settings['product_id'])] == 5
    assert response.json["is_available"] is True
    assert response.json["quantity"] == 100
    assert response.json["unique_products"] == 1


def test_unauth_user_add_product_with_quantity_negative(client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': -11}
    with client_with_products:
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert not session.get('shopping_cart').get(str(product_settings['product_id']), None)
    assert response.json["is_available"] is True
    assert response.json["unique_products"] == 0


def test_unauth_user_add_product_with_quantity_more_than_available(client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': 150}
    with client_with_products:
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert session['shopping_cart'][str(product_settings['product_id'])] == 100
    assert response.json["is_available"] is False
    assert response.json["quantity"] == 100
    assert response.json["unique_products"] == 1


def test_unauth_user_delete_product_from_cart(client_with_products, json_settings):
    product_settings_for_add = {'product_id': 1, 'quantity': 10}
    product_settings = {'product_id': 1, 'quantity': 0}
    with client_with_products:
        client_with_products.post('/add_to_cart', data=json.dumps(product_settings_for_add), headers=json_settings)
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert not session.get('shopping_cart').get(str(product_settings['product_id']), None)
    assert response.json["is_available"] is True
    assert response.json["quantity"] == 100
    assert response.json["unique_products"] == 0


def test_unauth_user_add_two_times_same_product_in_cart(client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': 1}
    product2_settings = {'product_id': 1, 'quantity': 5}
    client_with_products.post('/add_to_cart', data=json.dumps(product2_settings), headers=json_settings)
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    assert response.json["unique_products"] == 1


def test_unauth_user_add_two_different_products_in_cart(client_with_products, json_settings):
    product_settings = {'product_id': 2, 'quantity': 5}
    product2_settings = {'product_id': 1, 'quantity': 7}
    with client_with_products:
        client_with_products.post('/add_to_cart', data=json.dumps(product2_settings), headers=json_settings)
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
        assert session['shopping_cart'][str(product_settings['product_id'])] == 5
        assert session['shopping_cart'][str(product2_settings['product_id'])] == 7
    assert response.json["unique_products"] == 2


def test_auth_user_add_product_with_quantity_1(client_with_user, client_with_loggined_user, client_with_products,
                                               json_settings):
    product_settings = {'product_id': 1, 'quantity': 1}
    with client_with_products:
        assert current_user.is_authenticated
        if session.get('shopping_cart', None):
            del session['shopping_cart']
        response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    product_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).first()
    assert product_in_cart.quantity == 1
    assert response.json["is_available"] is True
    assert response.json["quantity"] == 100
    assert response.json["unique_products"] == 1


def test_auth_user_add_product_with_quantity_5(client_with_user, client_with_loggined_user, client_with_products,
                                               json_settings):
    product_settings = {'product_id': 1, 'quantity': 5}
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    product_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).first()
    assert product_in_cart.quantity == 5
    assert response.json["is_available"] is True
    assert response.json["unique_products"] == 1


def test_auth_user_add_product_with_quantity_negative(client_with_user, client_with_loggined_user, client_with_products,
                                                      json_settings):
    product_settings = {'product_id': 1, 'quantity': -11}
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    product_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
    assert product_in_cart == []
    assert response.json["is_available"] is True
    assert response.json["unique_products"] == 0


def test_auth_user_add_product_with_quantity_more_than_available(client_with_user, client_with_loggined_user,
                                                                 client_with_products, json_settings):
    product_settings = {'product_id': 1, 'quantity': 950}
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).first()
    assert products_in_cart.quantity == 100
    assert response.json["is_available"] is False
    assert response.json["unique_products"] == 1


def test_auth_user_delete_product_from_cart(client_with_user, client_with_loggined_user, client_with_products,
                                            json_settings):
    product_settings = {'product_id': 1, 'quantity': 0}
    product_settings_for_add_product = {'product_id': 1, 'quantity': 10}
    client_with_products.post('/add_to_cart', data=json.dumps(product_settings_for_add_product), headers=json_settings)
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    product_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
    assert product_in_cart == []
    assert response.json["unique_products"] == 0


def test_auth_user_add_two_different_products_in_cart(client_with_user, client_with_loggined_user, client_with_products,
                                                      json_settings):
    product_settings = {'product_id': 2, 'quantity': 5}
    product2_settings = {'product_id': 1, 'quantity': 7}
    client_with_products.post('/add_to_cart', data=json.dumps(product2_settings), headers=json_settings)
    response = client_with_products.post('/add_to_cart', data=json.dumps(product_settings), headers=json_settings)
    assert response.json["unique_products"] == 2
