from flask import Blueprint, render_template

from webapp.marketplace.models import Product

blueprint = Blueprint('marketplace', __name__)

@blueprint.route('/')
def index():
    title = "Каталог товаров"
    get_all_products = Product.query.all()
    return render_template('marketplace/index.html', page_title=title, products_list=get_all_products)
