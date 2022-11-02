from uuid import uuid4
from datetime import datetime

import requests
from flask import Blueprint, flash, render_template, redirect, url_for, abort, request, jsonify, session, Markup
from flask_login import current_user, login_required

from webapp.db import db
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser, UserRole
from webapp.marketplace.forms import AddNewProductForm, SearchForm, CheckoutForm, SortingProductForm
from webapp.marketplace.models import Category, Product, Photo, ShoppingCart, UserFavoriteProduct, ShoppingOrder
from webapp.services.service_photo import is_extension_allowed, save_files
from webapp.services.service_cart import (get_product_by_id, search_products_by_text, get_products_in_cart,
                                          get_number_of_unique_products_in_cart,
                                          save_products_into_db_from_session_cart,
                                          save_unauthenticated_user_data_in_session)
from webapp.services.service_favorite_product import is_user_add_product_to_favorite
from webapp.services.service_payment_process import prepare_link_for_payment, is_order_paid
from webapp.services.service_send_email import send_email
from webapp.services.service_sorting import process_sorting_product_types
from webapp.services.service_count import count_favorite_products_current_user

blueprint = Blueprint('marketplace', __name__)


@blueprint.route('/')
def index():
    title = "Каталог товаров"
    sorting_product_form = SortingProductForm()
    products_in_cart = get_products_in_cart()
    user_sorting_type = request.args.get('type_sorting')

    if user_sorting_type:
        try:
            products = process_sorting_product_types(user_sorting_type)
        except ValueError:
            flash("Не верный выбор сортировки")
            products = Product.query.all()
    else:
        products = Product.query.all()
    

    return render_template(
        'marketplace/index.html', 
        page_title=title, 
        products=products,
        products_in_cart=products_in_cart,
        is_user_add_product_to_favorite=is_user_add_product_to_favorite,
        sorting_product_form=sorting_product_form,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


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


@blueprint.route('/livesearch', methods=['POST'])
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

        unique_products_in_cart = get_number_of_unique_products_in_cart()
        session.modified = True

    # Если пользователь авторизован
    else:
        # Удаление товара из корзины
        if user_quantity <= 0:
            delete_product_from_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                                 ShoppingCart.product_id == current_product_id).delete()
            db.session.commit()
            unique_products_in_cart = get_number_of_unique_products_in_cart()
            return jsonify({"is_available": available_status, "quantity": product_quantity,
                            "unique_products": unique_products_in_cart})
        product_handler = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                    ShoppingCart.product_id == current_product_id).first()
        unique_products_in_cart = get_number_of_unique_products_in_cart()
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
        query_products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                           ShoppingCart.is_shopping_cart_paid == False).all()
        if query_products_in_cart:
            products_in_cart = {product.product_info: product.quantity for product in query_products_in_cart}
        else:
            products_in_cart = None
    else:
        products_in_cart = session.get('shopping_cart', None)
        if products_in_cart:
            products_in_session_cart = {int(prod_id): quantity for prod_id, quantity in products_in_cart.items()}
            query_products = Product.query.filter(Product.id.in_(products_in_session_cart.keys())).all()
            products_in_cart = {product: products_in_session_cart[product.id] for product in query_products}

    count_all_products = 0
    count_total_money = 0

    if products_in_cart:
        count_all_products = sum(products_in_cart.values())
        count_total_money = sum({product.price * quantity for product, quantity in products_in_cart.items()})
        session['count_all_products'] = count_all_products
        session['count_total_money'] = count_total_money

    return render_template(
        'marketplace/cart.html', 
        page_title=title,
        products_in_cart=products_in_cart,
        count_all_products=count_all_products,
        count_total_money=count_total_money,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


@blueprint.route('/del_product_from_cart/<int:product_id>')
def del_product_from_cart(product_id):
    if not current_user.is_authenticated:
        del session['shopping_cart'][str(product_id)]
        session.modified = True
    else:
        delete_product_from_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                             ShoppingCart.product_id == product_id,
                                                             ShoppingCart.is_shopping_cart_paid == False).delete()
        db.session.commit()
    return redirect(url_for('marketplace.cart'))


@blueprint.route('/checkout')
def checkout_page():
    title = 'Оформление заказа'
    form = CheckoutForm(obj=current_user)
    count_all_products = session.get('count_all_products', 0)
    count_total_money = session.get('count_total_money', 0)

    return render_template(
        'marketplace/checkout.html', 
        page_title=title, 
        form=form,
        count_all_products=count_all_products, 
        count_total_money=count_total_money,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


@blueprint.route('/checkout_process', methods=['POST'])
def checkout_process():
    form = CheckoutForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()

        if user == current_user:
            user.phone_number = form.phone_number.data
            user.shipping_adress = form.shipping_adress.data
            user.full_name = form.full_name.data
            db.session.commit()
            user_id = user.id

        elif user and user != current_user:
            save_unauthenticated_user_data_in_session(form)
            flash(Markup(f'''Пользователь с таким email зарегистрирован в системе. 
            Чтобы продолжить оформление заказа <a href="{url_for('user.login', next=url_for('marketplace.cart'))}" class="alert-link">Войдите в аккаунт</a>. 
            Товары в корзине и Ваши данные  будут сохранены'''))
            return redirect(url_for('marketplace.checkout_page'))

        elif not user:
            user_by_phone = User.query.filter(User.phone_number == form.phone_number.data).first()
            if not user_by_phone:
                create_user = User(email=form.email.data, phone_number=form.phone_number.data,
                                   shipping_adress=form.shipping_adress.data, full_name=form.full_name.data,
                                   role=UserRole.user)
                generated_user_password = str(uuid4())
                create_user.set_password(generated_user_password)
                db.session.add(create_user)
                db.session.commit()
                send_email(EmailEventsForUser.letter_with_account_password, create_user,
                           password=generated_user_password)
                user_id = create_user.id
                save_products_into_db_from_session_cart(create_user)
            else:
                save_unauthenticated_user_data_in_session(form)
                flash(Markup(f'''Пользователь с таким телефоном зарегистрирован в системе. 
                Чтобы продолжить оформление заказа <a href="{url_for('user.login', next=url_for('marketplace.cart'))}" class="alert-link">Войдите в аккаунт</a>.
                Товары в корзине и Ваши данные  будут сохранены'''))
                return redirect(url_for('marketplace.checkout_page'))

        return redirect(url_for('marketplace.payment_process', user_id=user_id))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Исправьте ошибку в поле {getattr(form, field).label.text}: {error}')

    return redirect(url_for('marketplace.checkout_page'))


@blueprint.route('/payment_process/<int:user_id>')
def payment_process(user_id):
    shopping_cart = ShoppingCart.query.filter(ShoppingCart.user_id == user_id,
                                              ShoppingCart.is_shopping_cart_paid == False).all()
    order_number = str(uuid4())
    payment_amount = sum([product.quantity * product.product_info.price for product in shopping_cart])

    new_order = ShoppingOrder(order_id=order_number, user_id=user_id, amount=payment_amount,
                              is_order_paid=False)
    db.session.add(new_order)
    db.session.commit()

    if not current_user.is_authenticated:
        session['order_number'] = order_number
        session.modified = True

    try:
        payment_link = prepare_link_for_payment(payment_amount, order_number)
    except requests.RequestException:
        payment_status = 'Оплата временно не доступна'
        return render_template('marketplace/payment_unavailable.html', payment_status=payment_status)

    return redirect(payment_link, code=302)


@blueprint.route('/check_payment', methods=['POST'])
def check_payment():
    if current_user.is_authenticated:
        shopping_order = ShoppingOrder.query.filter(ShoppingOrder.user_id == current_user.id,
                                                    ShoppingOrder.is_order_paid == False).all()
    else:
        order_number = session.get('order_number', None)
        shopping_order = ShoppingOrder.query.filter(ShoppingOrder.order_number == order_number,
                                                    ShoppingOrder.is_order_paid == False).all()

    shopping_order = shopping_order[-1]
    order_number = shopping_order.order_number
    payment_status = False

    if order_number:
        try:
            payment_status = is_order_paid(order_number)
        except requests.RequestException:
            pass

    if payment_status:
        if not current_user.is_authenticated:
            del session['shopping_cart']
            del session['count_all_products']
            del session['count_total_money']
            session.modified = True

        shopping_order.is_order_paid = True
        shopping_order.paid_datetime = datetime.now()
        paid_products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == shopping_order.user.id,
                                                          ShoppingCart.is_shopping_cart_paid == False).all()
        for product in paid_products_in_cart:
            product.order_id = shopping_order.id
            product.is_shopping_cart_paid = True

        db.session.commit()
        send_email(EmailEventsForUser.order_successfully_paid, shopping_order.user)

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

    return render_template(
        'marketplace/product_page.html', 
        page_title='Карточка товара',
        product=product, 
        products_in_cart=products_in_cart,
        is_user_add_product_to_favorite=is_user_add_product_to_favorite,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


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

    return render_template(
        'marketplace/category_page.html',
        page_title=title,
        products=products,
        products_in_cart=products_in_cart,
        is_user_add_product_to_favorite=is_user_add_product_to_favorite,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


@login_required
@blueprint.route('/add_product')
def add_product():
    title = 'Добавить товар'
    form = AddNewProductForm()
    return render_template(
        'marketplace/add_product.html', 
        page_title=title, 
        form=form,
        count_favorite_products_current_user=count_favorite_products_current_user
    )


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
        products_in_cart = get_products_in_cart()

        return render_template(
            'marketplace/favorite_page.html',
            page_title=title,
            products=products,
            is_user_add_product_to_favorite=is_user_add_product_to_favorite,
            products_in_cart=products_in_cart,
            count_favorite_products_current_user=count_favorite_products_current_user
        )
    else:
        flash("Чтобы перейти в список желаемого, необходимо авторизоваиться")
        return redirect(request.referrer)
