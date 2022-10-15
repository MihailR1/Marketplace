from flask import Blueprint, flash, render_template, redirect, url_for, abort, request, jsonify
from flask_login import current_user, login_required

from webapp.marketplace.forms import AddNewProductForm
from webapp.marketplace.models  import Product, Photo, Category, Favorite
from webapp.db import db
from webapp.marketplace.forms import AddNewProductForm, SearchForm
from webapp.marketplace.models import Category, Product, Photo
from webapp.services.service_photo import is_extension_allowed, save_files

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
            found_products = Product.query.filter(Product.name.ilike(f'%{search_string}%')).all()
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
        query_to_db = Product.query.filter(Product.name.ilike(f'%{search_text}%')).all()
        result = [(category.name, category.id) for category in query_to_db]
        return jsonify(result)


@blueprint.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.filter(Product.id == product_id).first()
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


@login_required
@blueprint.route('/favorite_product/<int:product_id>/<action>')
def favorite_product(product_id, action):
    product = Product.query.filter_by(id=product_id).first_or_404()
    if action == 'add_favorite':
        favorite = Favorite(user_id=current_user.id, product_id=product.id)
        db.session.add(favorite)
        db.session.commit()
    if action == 'del_favorite':
        favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).delete()
        db.session.commit()
    return redirect(request.referrer)


@login_required
@blueprint.route('/favorite')
def favorite():
    title = "Избранное"
    products = Product.query.filter(Product.id == Favorite.product_id, Favorite.user_id == current_user.id).all()
    return render_template('marketplace/favorite_page.html', page_title=title, products=products)