"""
Данные из json и сохраняет в БД за 1 раз
"""
import json

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Category


def data_from_json():
    with open('category_tree.json', encoding='utf-8') as file:
        data = json.load(file)

    return data


def get_last_id(data):
    if data == {}:
        return 0
    for number in sorted(data.values(), reverse=True):
        return number


def save_categories(json_data):
    db_data = Category.query.filter(Category.name.isnot(None)).all()
    category_name_and_id = {category.name: category.id for category in db_data}

    for main_category, dict_sub in json_data.items():
        category_id = category_name_and_id.get(main_category, None)
        if not category_id:
            category = Category(name=main_category)
            db.session.add(category)
            last_id_in_dict = get_last_id(category_name_and_id)
            category_name_and_id[main_category] = last_id_in_dict + 1

        for sub1_category, sub2_list in dict_sub.items():
            category_id = category_name_and_id.get(sub1_category, None)
            if not category_id:
                category = Category(name=sub1_category, parent_id=category_name_and_id[main_category])
                db.session.add(category)
                last_id_in_dict = get_last_id(category_name_and_id)
                category_name_and_id[sub1_category] = last_id_in_dict + 1

            for sub2_category in sub2_list:
                category_id = category_name_and_id.get(sub2_category, None)
                if not category_id:
                    category = Category(name=sub2_category, parent_id=category_name_and_id[sub1_category])
                    db.session.add(category)
                    last_id_in_dict = get_last_id(category_name_and_id)
                    category_name_and_id[sub2_category] = last_id_in_dict + 1

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        data_json = data_from_json()
        save_categories(data_json)
