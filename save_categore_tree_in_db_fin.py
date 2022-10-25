"""
Файл сохраняет дерево категорий из файла в БД
"""

import pandas as pd
from loguru import logger

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Category


def categories_name_and_id() -> dict:
    categories = Category.query.all()
    category_name_and_id = {category.name: category.id for category in categories}
    return category_name_and_id


@logger.catch
def save_root_categories(file) -> None:
    category_name_and_id = categories_name_and_id()

    for main_category in file.main.unique():
        if main_category not in category_name_and_id.keys():
            category = Category(name=main_category)
            db.session.add(category)
    db.session.commit()


@logger.catch
def save_categories(file) -> None:
    category_name_and_id = categories_name_and_id()
    last_id = max(category_name_and_id.values())

    for _, main, sub1_category, sub2_category, sub3_category, *_ in file.itertuples():
        category_id_sub1 = category_name_and_id.get(sub1_category, None)
        category_id_sub2 = category_name_and_id.get(sub2_category, None)
        category_id_sub3 = category_name_and_id.get(sub3_category, None)

        if not category_id_sub1:
            category = Category(name=sub1_category, parent_id=category_name_and_id[main])
            db.session.add(category)
            last_id += 1
            category_name_and_id[sub1_category] = last_id

        if not category_id_sub2 and sub2_category != '':
            category = Category(name=sub2_category, parent_id=category_name_and_id[sub1_category])
            db.session.add(category)
            last_id += 1
            category_name_and_id[sub2_category] = last_id

        if not category_id_sub3 and sub3_category != '':
            category = Category(name=sub3_category, parent_id=category_name_and_id[sub2_category])
            db.session.add(category)
            last_id += 1
            category_name_and_id[sub3_category] = last_id

    db.session.commit()


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        logger.info('Запустили процесс сохранения категорий в БД')
        category_tree_data = pd.read_excel('catalog.xlsx', na_filter=False)
        save_root_categories(category_tree_data)
        save_categories(category_tree_data)
        logger.info('Сохранение категорий в БД закончено')
