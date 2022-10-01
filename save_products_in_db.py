"""
Файл сохраняет данные из файла в БД
"""
import json

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Product, Category

app = create_app()


def products_to_db(id, name, price, description):
    product_exist = Product.query.filter(Product.id == id).count()

    if not product_exist:
        product_handler = Product(name=name, user_id=1,
                                  price=price, description=description, photos_path='../../static/images/0.png',
                                  category_id=2, color='Натуральный', size='Натуральный')

        db.session.add(product_handler)
        db.session.commit()


def save_products(json_file):
    # Создание категории и подкатегории в БД
    db.session.add(Category(name="Продкуты"))
    db.session.add(Category(name="Фрукты", parent_id=1))
    db.drop_all()
    db.create_all()
    db.session.commit()

    # Чтение json файла и сохранение в переменную
    with open(json_file, 'r', encoding='utf-8') as file:
        products_json = json.load(file)

    for product in products_json:
        item = products_json[product]
        name = item['name']
        price = item['cost']
        id = product
        description = item['description']

        products_to_db(id, name, price, description)


with app.app_context():
    save_products('products.json')
