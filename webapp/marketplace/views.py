from flask import Blueprint, render_template


blueprint = Blueprint('marketplace', __name__)

@blueprint.route('/')
def index():
    title = "Каталог товаров"

    return render_template('marketplace/index.html', page_title=title)