from webapp.marketplace.enums import ProductSortingTypes
from webapp.marketplace.models import Product


def process_sorting_product_types(user_sorting_type):
    user_sorting_type = ProductSortingTypes(user_sorting_type)

    if user_sorting_type == ProductSortingTypes.price_from_min_to_max:
        products = Product.query.order_by(Product.price).limit(20)
    elif user_sorting_type == ProductSortingTypes.price_from_max_to_min:
        products = Product.query.order_by(Product.price.desc()).limit(20)

    return products
