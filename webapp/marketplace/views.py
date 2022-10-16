from flask import Blueprint, flash, render_template, redirect, url_for, abort, request, jsonify, session
from flask_login import current_user, login_required

from webapp.db import db
from webapp.marketplace.forms import AddNewProductForm, SearchForm
from webapp.marketplace.models import Category, Product, Photo, ShoppingCart
from webapp.services.service_photo import is_extension_allowed, save_files
from webapp.services.cached_queries_to_db import (get_product_by_id, search_products_by_text,
                                                  number_of_unique_products_in_cart)

blueprint = Blueprint('marketplace', __name__)


@blueprint.route('/')
def index():
    title = "Каталог товаров"
    products = Product.query.all()
    return render_template('marketplace/index.html', page_title=title, products=products)


@blueprint.route('/search', methods=['POST'])
def search_result():
    form = SearchForm()
    if form.validate_on_submit():
        found_products = []
        search_string = form.search_input.data.lower()

        if search_string:
            found_products = search_products_by_text(search_string)
            title = f'По запросу «{search_string}» найдено {len(found_products)} товаров'
            return render_template('search.html', page_title=title, products=found_products)

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
    if request.method == 'POST':
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
        unique_products_in_cart = session['unique_products_in_cart']
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
            unique_products_in_cart = number_of_unique_products_in_cart(current_user.id)
            return jsonify({"is_available": available_status, "quantity": product_quantity,
                            "unique_products": unique_products_in_cart})

        product_handler = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id,
                                                    ShoppingCart.product_id == current_product_id).first()
        unique_products_in_cart = number_of_unique_products_in_cart(current_user.id)
        # Если продукта нет в корзине
        if not product_handler:
            save_product_in_cart = ShoppingCart(user_id=current_user.id, product_id=current_product_id,
                                                quantity=user_quantity, price=product_query.price)
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
        products_in_cart = ShoppingCart.query.filter(ShoppingCart.user_id == current_user.id).all()
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
    return render_template('marketplace/cart.html', page_title=title, products_in_cart=products_in_cart)


@blueprint.route('/product/<int:product_id>')
def product_page(product_id):
    product = get_product_by_id(product_id)
    if not product:
        abort(404)
    return render_template('marketplace/product_page.html', page_title='Карточка товара', product=product)


@blueprint.route('/category/<int:category_id>')
def category_page(category_id):
    category = Category.query.filter(Category.id == category_id).first()
    children_categories = category.get_children().all()
    title = f'Раздел товаров: {category.name}'

    if children_categories:
        categories_id = [category.id for category in children_categories]
        categories_id.append(category_id)
        products = Product.query.filter(Product.category_id.in_(categories_id)).all()
    else:
        products = Product.query.filter(Product.category_id == category_id).all()
    if not category:
        abort(404)

    return render_template('marketplace/category_page.html', page_title=title, products=products)


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
