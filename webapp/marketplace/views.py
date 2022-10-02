from flask import abort, Blueprint, render_template

from webapp.marketplace.models import Product

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
