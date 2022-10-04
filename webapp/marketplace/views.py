import os
from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask import abort, Blueprint, render_template
from werkzeug.utils import secure_filename
from random import choice

from webapp.marketplace.forms import AddNewProductForm
from webapp.marketplace.models  import Product
from webapp.db import db
from webapp.config import UPLOAD_FOLDER, ALLOWED_IMAGE


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
        
        files = form.files_img.data

        new_product = Product(
            category_id = form.category.data,
            user_id = current_user.id,
            name=form.name.data,
            price = form.price.data,
            photos_path = ", ".join(get_path_file_and_save(files)),
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE


def get_path_file_and_save(files):
    
    photos_path = []

    for file_img in files:
        if allowed_file(file_img):
            file_name = secure_filename(file_img)
            prefix_lst = [choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(12)]
            prefix = ''.join(prefix_lst)
            file_name = f"{prefix}_{file_name}"
            open(os.path.join(UPLOAD_FOLDER, file_name), 'w')
            photos_path.append(UPLOAD_FOLDER + file_name)
        else:
            flash('Можно добавить изображения с расширеним png, jpg, jpeg')
            return redirect(url_for('marketplace.add_product'))
    
    return photos_path
