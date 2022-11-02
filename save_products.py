"""
Файл сохраняет товары из файла в БД
"""
import os

import requests
import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from tenacity import retry, wait_fixed, stop_after_attempt

from webapp import create_app
from webapp.db import db
from webapp.config import UPLOAD_PATH
from webapp.user.enums import UserRole
from webapp.user.models import User
from webapp.marketplace.models import Product, Category, Photo

load_dotenv()


def dataframe_from_excel(data) -> pd.DataFrame:
    columns_name = ['main', 'sub1', 'sub2', 'sub3', 'Для кого', 'Заголовок', 'Цена', 'Наличие', 'Остаток', 'Описание',
                    'Изображения', 'Производитель', 'Ссылка на товар', 'Размер', 'Цвет', 'Страна', 'Состав',
                    'Материалы', 'Размер обуви', 'Сезон', 'Особенности', 'Основной состав']
    products_frame = pd.DataFrame(data, columns=columns_name)

    return products_frame


def get_or_create_admin() -> User:
    admin = User.query.filter(User.role == UserRole.admin).first()
    if not admin:
        admin = User(email=os.environ['ADMIN_EMAIL'], role=UserRole.admin)
        admin.set_password(os.environ['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
    return admin


def category_id_for_product(row, categories_name_and_id) -> int:
    if row['sub3']:
        return categories_name_and_id[row['sub3']]
    if row['sub2']:
        return categories_name_and_id[row['sub2']]

    return categories_name_and_id[row['sub1']]


@logger.catch
def save_products(products_frame) -> None:
    products = Product.query.all()
    categories = Category.query.all()
    admin = get_or_create_admin()
    product_and_id = {product.name: product.id for product in products}
    category_and_id = {category.name: category.id for category in categories}

    for _, row in products_frame.iterrows():
        if row['Заголовок'] not in product_and_id.keys():
            category_id = category_id_for_product(row, category_and_id)
            product = Product(
                category_id=category_id,
                user_id=admin.id,
                name=row['Заголовок'],
                price=row['Цена'],
                description=row['Описание'],
                brand_name=row['Производитель'],
                color=row['Цвет'],
                gender=row['Для кого'],
                size=row['Размер'],
                quantity=row['Остаток'],
            )
            db.session.add(product)

    db.session.commit()


@retry(wait=wait_fixed(3), stop=stop_after_attempt(3))
def response_for_photo(photo_url):
    photo_response = requests.get(photo_url)
    photo_response.raise_for_status()
    return photo_response


def save_photos_in_path(photos_url, product_id) -> list:
    photos_url_list = photos_url.split(';')
    list_with_photos_path = []

    for index, photo_url in enumerate(photos_url_list):
        photo_extension = photo_url.split('.')[-1]

        try:
            photo_response = response_for_photo(photo_url)
        except requests.RequestException as error:
            logger.exception(f'Ошибка обращения к фотографии продукта {error}')
            continue

        product_path = os.path.join(UPLOAD_PATH, f'product_{product_id}')
        os.makedirs(product_path, exist_ok=True)
        target_name_and_path_for_product = os.path.join(product_path, f'{index}.{photo_extension}')
        list_with_photos_path.append(target_name_and_path_for_product)

        with open(target_name_and_path_for_product, 'wb') as photo_path:
            photo_path.write(photo_response.content)

    return list_with_photos_path


@logger.catch
def save_photos_for_products(products_frame) -> None:
    products = Product.query.all()
    product_and_id = {product.name: product.id for product in products}

    for _, row in products_frame.iterrows():
        product_id = product_and_id.get(row['Заголовок'], None)

        if product_id:
            photos_path = save_photos_in_path(row['Изображения'], product_id)
            for path in photos_path:
                photo_product = Photo(product_id=product_id, photos_path=path)

                db.session.add(photo_product)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        logger.info('Запустили процесс сохранения товаров в БД')
        products_data = pd.read_excel('catalog.xlsx', na_filter=False)
        products_frame = dataframe_from_excel(products_data)
        save_products(products_frame)
        logger.info('Запустили процесс сохранения фото для товаров в БД')
        save_photos_for_products(products_frame)
        logger.info('Сохранение товаров и фото закончено')
