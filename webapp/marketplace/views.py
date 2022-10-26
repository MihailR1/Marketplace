from uuid import uuid4

import requests
from flask import Blueprint, flash, render_template, redirect, url_for, abort, request, jsonify, session
from flask_login import current_user, login_required

from webapp.db import db
from webapp.marketplace.forms import AddNewProductForm, SearchForm
from webapp.marketplace.models import Category, Product, Photo, ShoppingCart, UserFavoriteProduct, ShoppingOrder
from webapp.services.service_photo import is_extension_allowed, save_files
from webapp.services.service_cart import (get_product_by_id, search_products_by_text, get_products_in_cart,
                                          get_unique_products_in_cart)
from webapp.services.service_favorite_product import is_user_add_product_to_favorite
from webapp.services.service_payment_process import prepare_link_for_payment, is_order_paid

blueprint = Blueprint('marketplace', __name__)


@blueprint.route('/')
def index():
    title = "Каталог товаров"
    products = Product.query.all()
    products_in_cart = get_products_in_cart()
    return render_template('marketplace/index.html', page_title=title, products=products,
                           products_in_cart=products_in_cart,
                           is_user_add_product_to_favorite=is_user_add_product_to_favorite)


@blueprint.route('/search', methods=['POST'])
def search_result():
    form = SearchForm()
    if form.validate_on_submit():
        found_products = []
        search_string = form.search_input.data.lower()
        products_in_cart = get_products_in_cart()

        if search_string:
            found_products = search_products_by_text(search_string)
            title = f'По запросу «{search_string}» найдено {len(found_products)} товаров'
            return render_template('search.html', page_title=title, products=found_products,
                                   is_user_add_product_to_favorite=is_user_add_product_to_favorite,
                                   products_in_cart=products_in_cart)

        if not found_products or not search_string:
            title = 'Не нашли подходящих товаров'
            return render_template('search.html', page_title=title)

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {getattr(form, field).label.text}: {error}')
    return redirect(url_for('marketplace.index'))


@blueprint.route("/livesearch", methods=['POST'])
def livesearch():
    if request.method == 'POST':
        search_text = request.form['search'].lower()
        query_to_db = search_products_by_text(search_text)
        result = [(category.name, category.id) for category in query_to_db]
        return jsonify(result)


@blueprint.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    request_handler = request.get_json()
    current_product_id = request_handler['product_id']
    user_quantity = request_handler['quantity']
    product_query = get_product_by_id(current_product_id)
    product_quantity = product_query.quantity
    available_status = True

    # Если не авторизован, то корзина хранится в сессии
    if not current_user.is_authenticated:
        if 'shopping_cart' not in session:
            session['shopping_cart'] = {}

        session['shopping_cart'][str(current_product_id)] = user_quantity
        if user_quantity <= 0:
            del session['shopping_cart'][str(current_product_id)]

        elif user_quantity > product_quantity:
            session['shopping_cart'][str(current_product_id)] = product_quantity
            available_status = False

        session['unique_products_in_cart'] = len(session['shopping_cart'])
        unique_products_in_cart = get_unique_products_in_cart()
        session.modified = True

    # Если пользователь авторизован
    else:
        # Удаление товара из корзины
        if user_quantity <= 0:
            delete_product_from_cart = ShoppingCart.query.filter(
                ShoppingCart.user_id == current_user.id,
                ShoppingCart.product_id == current_product_id
            ).delete()
            db.session.commit()
            unique_products_in_cart = get_unique_products_in_cart()
            return jsonify({"is_available": available_status, "quantity": product_quantity,
                            "unique_products": unique_products_in_cart})
        product_handler = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                    ShoppingCart.product_id == current_product_id).first()
        unique_products_in_cart = get_unique_products_in_cart()
        # Если продукта нет в корзине
        if not product_handler:
            save_product_in_cart = ShoppingCart(user_id=current_user.id, product_id=current_product_id,
                                                quantity=user_quantity)
            db.session.add(save_product_in_cart)
            db.session.commit()
            unique_products_in_cart += 1
        # Если продукт в корзине, то меняет количество
        else:
            # Если юзер запросил больше, чем есть в наличии
            if user_quantity > product_quantity:
                product_handler.quantity = product_quantity
                available_status = False
            else:
                product_handler.quantity = user_quantity
            db.session.commit()

    return jsonify({"is_available": available_status, "quantity": product_quantity,
                    "unique_products": unique_products_in_cart})


@blueprint.route('/cart')
def cart():
    title = 'Корзина товаров'
    if current_user.is_authenticated:
        query_products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
        if query_products_in_cart:
            products_in_cart = {product.product_info: product.quantity for product in query_products_in_cart}
        else:
            products_in_cart = None
    else:
        products_in_cart = session.get('shopping_cart', None)
        if products_in_cart:
            products_id = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}
            query_products = Product.query.filter(Product.id.in_(products_id.keys())).all()
            products_in_cart = {}
            for product in query_products:
                for id_product, quantity in products_id.items():
                    if product.id == int(id_product):
                        products_in_cart[product] = quantity
                        break
    count_all_products = 0
    count_total_money = 0

    if products_in_cart:
        count_all_products = sum(products_in_cart.values())
        count_total_money = sum({product.price * quantity for product, quantity in products_in_cart.items()})

    return render_template('marketplace/cart.html', page_title=title, products_in_cart=products_in_cart,
                           count_all_products=count_all_products, count_total_money=count_total_money)


@blueprint.route('/del_product_from_cart/<int:product_id>')
def del_product_from_cart(product_id):
    if not current_user.is_authenticated:
        del session['shopping_cart'][str(product_id)]
        session.modified = True
    else:
        delete_product_from_cart = ShoppingCart.query.filter(
            ShoppingCart.user_id == current_user.id,
            ShoppingCart.product_id == product_id
        ).delete()
        db.session.commit()
    return redirect(url_for('marketplace.cart'))


@blueprint.route('/payment_process/<int:payment_sum>')
def payment_process(payment_sum):
    # if current_user.is_authenticated:
    #     user_id = current_user.id
    # else:
    # session['user_id'] = str(uuid4())
    # new_order = ShoppingOrder(order_id=order_number, user_id=user_id, amount=payment_sum)
    # db.session.add(new_order)
    # db.session.commit()
    session['order_number'] = str(uuid4())
    order_number = session['order_number']

    try:
        payment_link = prepare_link_for_payment(payment_sum, order_number)
    except requests.RequestException:
        payment_status = 'Оплата временно не доступна'
        return render_template('marketplace/payment_status.html', payment_status=payment_status)

    return redirect(payment_link, code=302)


@blueprint.route('/check_payment', methods=['POST'])
def check_payment():
    order_number = session.get('order_number', None)
    payment_status = False

    if order_number:
        try:
            payment_status = is_order_paid(order_number)
        except requests.RequestException:
            pass

    if payment_status:
        try:
            del session['order_number']
            del session['shopping_cart']
            del session['unique_products_in_cart']
            session.modified = True
        except KeyError:
            pass
        if current_user.is_authenticated:
            delete_product_from_cart = ShoppingCart.query.filter(
                ShoppingCart.user_id == current_user.id).delete()
            db.session.commit()

    return jsonify({"payment_status": payment_status})


@blueprint.route('/payment_status')
def payment_status():
    payment_status = 'Проверяем платеж...'
    return render_template('marketplace/payment_status.html', payment_status=payment_status)


@blueprint.route('/product/<int:product_id>')
def product_page(product_id):
    product = get_product_by_id(product_id)
    products_in_cart = get_products_in_cart()
    if not product:
        abort(404)

    return render_template('marketplace/product_page.html', page_title='Карточка товара',
                           product=product, products_in_cart=products_in_cart,
                           is_user_add_product_to_favorite=is_user_add_product_to_favorite)


@blueprint.route('/category/<int:category_id>')
def category_page(category_id):
    category = Category.query.filter(Category.id == category_id).first()
    children_categories = category.get_children().all()
    products_in_cart = get_products_in_cart()
    title = f'Раздел товаров: {category.name}'

    if children_categories:
        categories_id = [category.id for category in children_categories]
        categories_id.append(category_id)
        products = Product.query.filter(Product.category_id.in_(categories_id)).all()
    else:
        products = Product.query.filter(Product.category_id == category_id).all()
    if not category:
        abort(404)

    return render_template('marketplace/category_page.html', page_title=title, products=products,
                           products_in_cart=products_in_cart,
                           is_user_add_product_to_favorite=is_user_add_product_to_favorite)


@login_required
@blueprint.route('/add_product')
def add_product():
    title = 'Добавить товар'
    form = AddNewProductForm()
    return render_template('marketplace/add_product.html', page_title=title, form=form)


@login_required
@blueprint.route('/process_add_product', methods=['POST'])
def process_add_product():
    form = AddNewProductForm()

    if form.validate_on_submit():

        photos = form.photos.data
        if is_extension_allowed(photos) == False:
            flash('Можно добавить изображения с расширеним png, jpg, jpeg')
            return redirect(url_for('marketplace.add_product'))

        photos_path = save_files(photos)

        new_product = Product(
            category_id=form.category.data,
            user_id=current_user.id,
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            brand_name=form.brand_name.data,
            color=form.color.data,
            gender=form.gender.data,
            size=form.size.data
        )

        db.session.add(new_product)
        db.session.commit()

        for path in photos_path:
            new_product_photo = Photo(
                product_id=new_product.id,
                photos_path=path
            )

            db.session.add(new_product_photo)
            db.session.commit()

        flash('Вы добавили товар')
        return redirect(url_for('marketplace.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash("Ошибка в поле {}: {}".format(
                    getattr(form, field).label.text,
                    error
                ))
    return redirect(url_for('marketplace.add_product'))


@login_required
@blueprint.route('/add_favorite_product/<int:product_id>')
def add_favorite_product(product_id):
    """Добавление товара в избранное"""

    product = Product.query.filter_by(id=product_id).first_or_404()
    favorite = UserFavoriteProduct(user_id=current_user.id, product_id=product.id)
    db.session.add(favorite)
    db.session.commit()
    return redirect(request.referrer)


@login_required
@blueprint.route('/del_favorite_product/<int:product_id>')
def del_favorite_product(product_id):
    """Удаление товара из избранного"""

    product = Product.query.filter_by(id=product_id).first_or_404()
    favorite = UserFavoriteProduct.query.filter_by(user_id=current_user.id, product_id=product.id).delete()
    db.session.commit()
    return redirect(request.referrer)


@login_required
@blueprint.route('/favorite')
def favorite_page():
    """Страница с понравившимся товаром пользователя"""

    title = "Избранное"
    if current_user.is_authenticated:
        products = Product.query.filter(Product.id == UserFavoriteProduct.product_id,
                                        UserFavoriteProduct.user_id == current_user.id).all()
        return render_template(
            'marketplace/favorite_page.html',
            page_title=title,
            products=products,
            is_user_add_product_to_favorite=is_user_add_product_to_favorite
        )
    else:
        return render_template(
            'marketplace/favorite_page.html', page_title=title)
