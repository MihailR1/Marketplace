"""
Файл сохраняет данные из файла в БД
"""
import json

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Product, Category

with open('products.json', 'r', encoding='utf-8') as file:
    PRODUCT_JSON = json.load(file)

app = create_app()

with app.app_context():
    def save_products(id, name, price, description, img):
        product_exist = Product.query.filter(Product.id == id).count()
        if not product_exist:
            product_handler = Product(id=id, name=name, user_id=1,
                                      price=price, description=description, photos_path=img,
                                      category_id=1, color='Натуральный', size='Натуральный')
            db.session.add(product_handler)
            db.session.commit()


    def get_products(json_file):
        for product in json_file:
            item = json_file[product]
            id = product
            name = item['name']
            price = item['cost']
            description = item['description']
            img_path = item['image']

            save_products(id, name, price, description, img_path)


    get_products(PRODUCT_JSON)
