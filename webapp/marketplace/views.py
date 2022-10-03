from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user, login_required

from webapp.marketplace.forms import AddNewProductForm
from webapp.model import Category, db, Product


blueprint = Blueprint('marketplace', __name__)

@blueprint.route('/')
def index():
    title = "Каталог товаров"
    return render_template('marketplace/index.html', page_title=title)


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