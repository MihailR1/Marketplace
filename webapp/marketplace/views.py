from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user

from webapp.marketplace.forms import AddNewProductForm
from webapp.model import Category, db, Product


blueprint = Blueprint('marketplace', __name__)

@blueprint.route('/')
def index():
    title = "Каталог товаров"
    return render_template('marketplace/index.html', page_title=title)


@blueprint.route('/add_product')
def add_product():
    if not current_user.is_authenticated:
        return redirect(url_for('marketplace.login'))
    title = 'Добавить товар'
    form = AddNewProductForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    return render_template('marketplace/add_product.html', page_title=title, form=form)


@blueprint.route('/process_add_product', methods=['POST'])
def process_add_product():
    form = AddNewProductForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        new_product = Product(
            category_id = form.category.data,
            user_id = current_user.id,
            name=form.name.data,
            price = form.price.data,
            photos_path = 'asdasdas',
            description = form.description.data,
            brand_name = form.brand_name.data,
            color = form.color.data,
            gender = form.gender.data,
            size = form.size.data
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