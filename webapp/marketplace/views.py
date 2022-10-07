from flask import Blueprint, flash, render_template, redirect, url_for, abort
from flask_login import current_user, login_required

from webapp import cache
from webapp.marketplace.forms import AddNewProductForm
from webapp.marketplace.models import Category, db, Product

blueprint = Blueprint('marketplace', __name__)


@blueprint.route('/')
def index():
    title = "Каталог товаров"
    products = Product.query.all()
    return render_template('marketplace/index.html', page_title=title, products=products)


@blueprint.route('/product/<int:product_id>')
def product_page(product_id):
    product = Product.query.filter(Product.id == product_id).first()

    if not product:
        abort(404)

    return render_template('marketplace/product_page.html', page_title='Карточка товара', product=product)

@cache.cached(timeout=18000, key_prefix='dropdown_categories')
@blueprint.context_processor
def utility_processor():
    def dropdown_categories():
        categories = Category.query.filter(Category.parent_id.is_(None)).all()
        result = [sub_categories for category in categories for sub_categories in category.drilldown_tree()]
        return result

    return dict(dropdown_categories=dropdown_categories)

@blueprint.route('/category/<int:category_id>')
def category_page(category_id):
    category = Category.query.filter(Category.id == category_id).first()
    products = Product.query.filter(Product.category_id == category_id).all()
    title = f'Раздел товаров: {category.name}'

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
        new_product = Product(
            category_id=form.category.data,
            user_id=current_user.id,
            name=form.name.data,
            price=form.price.data,
            photos_path='asdasdas',
            description=form.description.data,
            brand_name=form.brand_name.data,
            color=form.color.data,
            gender=form.gender.data,
            size=form.size.data
        )
        db.session.add(new_product)
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
