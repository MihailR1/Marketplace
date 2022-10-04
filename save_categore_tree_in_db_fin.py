"""
Файл сохраняет дерево категорий из файла в БД
"""

import pandas

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Category


def get_last_id(data):
    if data == {}:
        return 0
    for number in sorted(data.values(), reverse=True):
        return number


def save_categories(file):
    db_data = Category.query.filter(Category.name.isnot(None)).all()
    category_name_and_id = {category.name: category.id for category in db_data}

    for _, main, sub1_category, sub2_category, sub3_category, *_ in file.itertuples():
        category_id_main = category_name_and_id.get(main, None)
        category_id_sub1 = category_name_and_id.get(sub1_category, None)
        category_id_sub2 = category_name_and_id.get(sub2_category, None)
        category_id_sub3 = category_name_and_id.get(sub3_category, None)

        if not category_id_main:
            category = Category(name=main)
            db.session.add(category)
            last_id = get_last_id(category_name_and_id)
            category_name_and_id[main] = last_id + 1

        if not category_id_sub1:
            category = Category(name=sub1_category, parent_id=category_name_and_id[main])
            db.session.add(category)
            last_id = get_last_id(category_name_and_id)
            category_name_and_id[sub1_category] = last_id + 1

        if not category_id_sub2 and sub2_category != '':
            category = Category(name=sub2_category, parent_id=category_name_and_id[sub1_category])
            db.session.add(category)
            last_id = get_last_id(category_name_and_id)
            category_name_and_id[sub2_category] = last_id + 1

        if not category_id_sub3 and sub3_category != '':
            category = Category(name=sub3_category, parent_id=category_name_and_id[sub2_category])
            db.session.add(category)
            last_id = get_last_id(category_name_and_id)
            category_name_and_id[sub3_category] = last_id + 1

    db.session.commit()


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        category_tree_data = pandas.read_excel('category_tree.xlsx', na_filter=False)
        save_categories(category_tree_data)
