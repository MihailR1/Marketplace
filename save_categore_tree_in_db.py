"""
Файл сохраняет дерево категорий из файла в БД
"""

import pandas

from webapp import create_app
from webapp.db import db
from webapp.marketplace.models import Category

app = create_app()


def data_from_db():
    """
    Функция получает и возвращает актуальную информацию из БД
    (Чтобы не писать такой длинный запрос каждый раз)
    """
    
    return Category.query.filter(Category.name.isnot(None)).all()


def get_category_name_and_id(data_from_db):
    """
    Функция сохраняет в словарь название категории и номер id
    и возвращает словарь
    """
    
    result = {category.name: category.id for category in data_from_db}
    return result


def check_root_category(data_from_db):
    """
    Проверяет есть ли главный раздел в БД,
    если нету, то создает и возвращает его
    """
    
    root_category = None

    for category in data_from_db:
        if category.tree_id == 1 and category.parent_id is None:
            root_category = category

    if not root_category:
        root_category = Category(name="Root_catalog")
        db.session.add(root_category)
        db.session.commit()

    return root_category


def save_main_category(file, root_category, db_data):
    categories_name = get_category_name_and_id(db_data)

    for main_category in file.main.unique():
        if main_category not in categories_name.keys():
            main = Category(name=main_category, parent_id=root_category.id)
            db.session.add(main)

    db.session.commit()


def save_first_category_branch(file):
    actual_db_data = data_from_db()
    categories_name = get_category_name_and_id(actual_db_data)
    used_categories = set()

    for _, main, sub1_category, _ in file.itertuples():
        if sub1_category not in categories_name and sub1_category not in used_categories:
            result = Category(name=sub1_category, parent_id=categories_name[main])
            used_categories.add(sub1_category)
            db.session.add(result)

    db.session.commit()


def save_second_category_branch(file):
    actual_db_data = data_from_db()
    categories_name = get_category_name_and_id(actual_db_data)
    used_categories = set()

    for _, main, sub1_category, sub2_category in file.itertuples():
        if sub2_category not in categories_name and sub2_category not in used_categories:
            result = Category(name=sub2_category, parent_id=categories_name[sub1_category])
            used_categories.add(sub2_category)
            db.session.add(result)

    db.session.commit()


with app.app_context():
    category_tree_data = pandas.read_excel('category_tree.xlsx')
    db_data = data_from_db()
    root = check_root_category(db_data)
    save_main_category(category_tree_data, root, db_data)
    save_first_category_branch(category_tree_data)
    save_second_category_branch(category_tree_data)
