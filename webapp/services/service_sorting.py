from webapp.marketplace.enum import ProductSortingTypes
from webapp.marketplace.models import Product


def process_sorting_product_types(user_sorting_type):
    
    try:
        user_sorting_type = ProductSortingTypes(user_sorting_type)
    except ValueError:
        'Не верный тип сортировки'

    if user_sorting_type == ProductSortingTypes.price_from_min_to_max:
        products = Product.query.order_by(Product.price).all()
    elif user_sorting_type == ProductSortingTypes.price_from_max_to_min:
        products = Product.query.order_by(Product.price.desc()).all()
    
    return products
