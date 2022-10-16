from webapp.marketplace.models import User_favorite_product

def is_user_favorite_product(current_user, product):
    return User_favorite_product.query.filter(
        User_favorite_product.user_id == current_user.id, 
        User_favorite_product.product_id == product.id
    ).count() > 0


